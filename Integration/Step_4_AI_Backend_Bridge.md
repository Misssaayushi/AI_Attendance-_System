# Step 4: AI-to-Backend Attendance Bridge

## 🎯 Objective
Fix the AI Module's `api_service.py` so it successfully sends verified attendance events to the Backend's `/api/v1/attendance/mark` endpoint, resolving all type mismatches, authentication requirements, and schema differences.

---

## 📊 Current Mismatch Analysis

### AI Module Sends (Current)
```python
# api_service.py → AttendancePayload
{
    "student_id": "1",           # ❌ String — Backend expects int
    "name": "Aayushi",            # ❌ Not in Backend schema
    "confidence": 92.5,           # ❌ Scale 0-100 — Backend expects 0.0-1.0
    "timestamp": "2026-05-16T...",# ❌ Not in Backend schema
    "status": "Present"           # ✅ Correct
}
```

### Backend Expects (`AttendanceMarkRequest`)
```python
{
    "student_id": 1,              # int (required, > 0)
    "attendance_date": null,      # date (optional, defaults to today)
    "attendance_time": null,      # time (optional, defaults to now)
    "status": "Present",          # "Present" | "Absent" | "Late"
    "confidence_score": 0.925,    # float (optional, 0.0 to 1.0)
    "source": "ai_recognition"    # string (optional)
}
```

### Additional Issue: Authentication
The Backend's attendance routes are **protected** (`Depends(get_current_admin)`). The AI Module currently sends **no auth token**, so all requests will return **401 Unauthorized**.

---

## 📝 Implementation Tasks

### Task 4.1 — Create Backend Endpoint for AI Module (No Auth)

The AI Module is a **trusted internal service** running on the same machine. It should NOT need JWT admin credentials to mark attendance.

**Option A (Recommended)**: Create a separate **internal** attendance endpoint that uses an API key instead of JWT.

**File**: `backend/Backend/app/routes/attendance.py`

Add a new **unprotected** endpoint with API key validation:

```python
from fastapi import Header, HTTPException

INTERNAL_API_KEY = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")

@router.post("/verify", status_code=status.HTTP_201_CREATED)
def verify_attendance_from_ai(
    payload: attendance_schema.AIAttendancePayload,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    """
    Endpoint for AI Module to send verified attendance events.
    Uses API key authentication instead of JWT.
    """
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Convert AI payload to standard attendance mark request
    mark_request = attendance_schema.AttendanceMarkRequest(
        student_id=payload.student_id,
        status=attendance_schema.AttendanceStatus(payload.status),
        confidence_score=payload.confidence / 100.0,  # Convert 0-100 → 0.0-1.0
        source="ai_recognition",
    )
    
    record = attendance_service.mark_attendance(db, mark_request)
    return success_response(
        data={"id": record.id, "student_id": record.student_id, "status": record.status},
        message="Attendance verified and logged",
        status_code=201,
    )
```

> **Note**: This endpoint does NOT have `Depends(get_current_admin)`, but uses `X-API-Key` header for service-to-service authentication.

---

### Task 4.2 — Add AI Attendance Schema to Backend

**File**: `backend/Backend/app/schemas/attendance.py`

```python
class AIAttendancePayload(BaseModel):
    """Schema for incoming AI Module attendance events."""
    student_id: str  # AI sends string, we convert to int
    name: str
    confidence: float  # 0-100 scale
    timestamp: str  # ISO-8601
    status: str = "Present"

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v):
        try:
            int_id = int(v)
            if int_id <= 0:
                raise ValueError
            return v
        except (ValueError, TypeError):
            raise ValueError("student_id must be a positive integer string")
```

---

### Task 4.3 — Update AI Module Config

**File**: `ai-module/AI_Module/config.py`

```diff
 # API Integration Settings (Phase 6)
 API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
-ATTENDANCE_VERIFY_ENDPOINT = os.getenv("ATTENDANCE_VERIFY_ENDPOINT", "/api/v1/attendance/verify")
+ATTENDANCE_VERIFY_ENDPOINT = os.getenv("ATTENDANCE_VERIFY_ENDPOINT", "/api/v1/attendance/verify")
 ATTENDANCE_VERIFY_URL = f"{API_BASE_URL.rstrip('/')}{ATTENDANCE_VERIFY_ENDPOINT}"
+
+# API Authentication
+AI_MODULE_API_KEY = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")
```

---

### Task 4.4 — Update AI Module API Service to Send Auth Header

**File**: `ai-module/AI_Module/api_service.py`

Modify `_send_http()` to include the API key header:

```diff
 def __init__(self, ...):
     ...
+    self.api_key = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")

 def _send_http(self, payload):
     ...
     for attempt in range(1, attempts + 1):
         try:
             response = requests.post(
                 self.verify_url,
                 json=payload,
                 timeout=self.timeout_seconds,
+                headers={"X-API-Key": self.api_key},
             )
```

---

### Task 4.5 — Ensure student_id Mapping is Correct

The AI Module identifies students by folder name format: `{id}_{name}` (e.g., `1_Aayushi`).

In `recognize_faces.py` line 321:
```python
student_id = name.split("_")[0] if "_" in name else name
```

This extracts `"1"` from `"1_Aayushi"`. The Backend endpoint (Task 4.1) will convert this string `"1"` to integer `1` when creating the `AttendanceMarkRequest`.

**Critical**: The AI Module's dataset folder names **MUST** use the same ID as the MySQL `students.id` column. Step 3 handles this by naming folders `{student.id}_{student.first_name}`.

---

### Task 4.6 — Update .env Files for Both Services

**`backend/Backend/.env`**:
```env
AI_MODULE_API_KEY=your-secure-api-key-here
```

**`ai-module/AI_Module/.env`** (or set as environment variable):
```env
API_BASE_URL=http://127.0.0.1:8000
AI_MODULE_API_KEY=your-secure-api-key-here
API_MOCK_MODE=false
```

---

## 🔄 Complete Attendance Verification Flow (After Integration)

```
1. AI Module webcam detects a face
2. Face encoding is compared against known encodings
3. Match found: student_id="1", name="1_Aayushi", confidence=92.5
4. AttendanceManager verifies: passes cooldown check, stability check, confidence threshold
5. APIDispatcher sends async POST to Backend:
   URL: http://127.0.0.1:8000/api/v1/attendance/verify
   Headers: { "X-API-Key": "your-secure-api-key" }
   Body: { "student_id": "1", "name": "Aayushi", "confidence": 92.5, "timestamp": "...", "status": "Present" }
6. Backend /verify endpoint:
   - Validates API key
   - Converts student_id "1" → int 1
   - Converts confidence 92.5 → 0.925
   - Checks student exists in MySQL
   - Checks confidence >= 0.6 threshold
   - Checks no duplicate attendance for today
   - Creates attendance record
   - Returns 201 Created
7. AI Module overlay shows "Attendance Logged" in green
```

---

## ✅ Verification Checklist
- [ ] Backend `/api/v1/attendance/verify` endpoint created (API key auth)
- [ ] AI Module sends correct `X-API-Key` header
- [ ] student_id string→int conversion works
- [ ] confidence 0-100 → 0.0-1.0 conversion works
- [ ] Attendance record created in MySQL database
- [ ] Duplicate attendance prevention works (same student, same day)
- [ ] AI Module overlay shows success/failure feedback
- [ ] Mock mode (`API_MOCK_MODE=true`) still works for testing without Backend

---

## 📁 Files Changed
| File | Action |
|---|---|
| `backend/Backend/app/routes/attendance.py` | **MODIFY** — add `/verify` endpoint |
| `backend/Backend/app/schemas/attendance.py` | **MODIFY** — add `AIAttendancePayload` |
| `ai-module/AI_Module/config.py` | **MODIFY** — add `AI_MODULE_API_KEY` |
| `ai-module/AI_Module/api_service.py` | **MODIFY** — add API key header |
| `backend/Backend/.env` | **MODIFY** — add `AI_MODULE_API_KEY` |
