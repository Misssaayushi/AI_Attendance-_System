# Phase 5: Attendance Verification Logic — Implementation Plan

## 🧠 Senior AI Systems Engineer Perspective

### 1. The Verification Philosophy
Attendance is a high-stakes transaction. A "False Positive" (marking the wrong person) is a failure of integrity. Therefore, Phase 5 moves from simple matching to **Evidence-Based Verification**. 
- **Confidence Scoring**: We convert Euclidean distance into a 0-100% human-readable score.
- **Stability Window**: No one is marked present on a single frame. We require a "streak" of successful recognitions to confirm identity.
- **Anti-Duplicate Logic**: Using a cooldown system to ensure one student doesn't fill the logs with 500 entries in 5 minutes.

### 2. Recognition Reliability
To improve reliability, we will implement **Threshold Filtering**. If the AI matches a face but the confidence is 72% and our threshold is 85%, we display the name but *do not* verify the attendance.

### 3. Improving Accuracy
By implementing a **Per-User Cooldown**, we prevent the system from getting stuck in a loop. Once a student is verified, the system "ignores" their successful matches for a configurable period, saving processing power and keeping the UI clean.

---

## 📋 Detailed Plan

### 1. Attendance Verification Workflow
The workflow is a tiered decision tree:
1. Is a face detected?
2. Is it recognized?
3. Is confidence > `MIN_THRESHOLD`?
4. Has stability count been reached?
5. Is the user outside their cooldown period?
6. **VERIFY.**

### 2. Recognition Confidence Strategy
We will use a linear mapping: `Confidence = (1.0 - Distance) * 100`. 
- Distance 0.4 (Very close) ➔ 60% Confidence? No, distance 0.4 is actually very good.
- Distance 0.6 is the default limit. So `(1.0 - 0.6) * 100 = 40%`.
- We will normalize it so that 0.6 distance = 0% confidence and 0.2 distance = 100% confidence for better UX.

### 3. Threshold Validation Architecture
Centralized in `config.py` as `MIN_CONFIDENCE_THRESHOLD`. This allows the university to decide how strict they want to be.

### 4. Duplicate Detection Logic
Implemented via an `AttendanceManager` class using an in-memory dictionary `{student_id: last_verify_time}`.

### 5. Unknown Face Handling Strategy
Unknown faces are tracked separately. If an unknown face persists for many frames, we can log it as a "Security Alert" or simply ignore it.

### 6. Cooldown System Planning
- **Type**: Time-based.
- **Duration**: Configurable (e.g., 30 minutes).
- **Scope**: Per Student ID.

### 7. Error Handling Workflow
- Missing encoding file: Handled in Phase 4, but verified here.
- Camera disconnect: System fails gracefully and releases memory.

### 8. Future Backend Integration Preparation
Instead of writing to a database, we will return a `VerificationEvent` object. This object will be ready to be sent to a FastAPI `POST /attendance` endpoint in Phase 6.

### 9. Scalability Considerations
The in-memory cooldown dictionary can handle thousands of students with zero lag. 

### 10. Testing & Debugging Strategy
- **`test_verification.py`**: A dedicated script to simulate multiple scans and verify cooldown logic.
- **Debug Overlays**: Visual indicators showing "STABILITY: 3/5" or "COOLDOWN ACTIVE".

---

## 🛠️ Files to Create/Modify

### New Files
- `ai_module/attendance_logic.py`: The core verification manager.
- `ai_module/tests/test_verification.py`: Verification and cooldown tests.

### Modified Files
- `ai_module/config.py`: Add `MIN_CONFIDENCE_THRESHOLD`, `COOLDOWN_MINUTES`, `STABILITY_FRAMES`.
- `ai_module/utils.py`: Add `AttendanceManager` class.
- `ai_module/recognize_faces.py`: Update to use the verification logic.
