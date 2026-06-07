# Step 3: Student Registration Pipeline

## 🎯 Objective
Build a **complete registration pipeline** that flows:

```
Frontend Form → Backend API → Database (Student + Face Encoding) → AI Module Dataset Folder
```

Currently, registration exists in three disconnected pieces. This step wires them into one seamless flow.

---

## 📊 Current State

### Frontend (`Register.jsx`)
- Has a form with fields: fullName, studentId, email, contactNumber, department, batch, semester, section, gender, course
- Has WebcamFeed for face capture → stores `capturedImage` (base64 data URL)
- Calls `registerStudent()` which hits `POST /api/v1/students/register` ← **WRONG endpoint**
- Sends `{ ...formData, image_data: capturedImage }` ← **Schema mismatch**

### Backend (`POST /api/v1/students/`)
- Expects `StudentCreate` schema with fields: first_name, last_name, email, roll_number, etc.
- Does NOT accept `image_data` or `fullName`
- Does NOT create AI dataset folder
- Does NOT trigger face encoding

### AI Module (`register_face.py`)
- Uses **terminal input** (`input()`) to get student ID and name
- Opens webcam independently and captures 20 samples
- Saves to `dataset/{id}_{name}/sample_XX.jpg`
- Completely **separate** from Frontend/Backend

---

## 📝 Implementation Tasks

### Task 3.1 — Update Frontend Register Form Field Mapping

The Frontend form fields don't match the Backend schema. Fix the mapping:

| Frontend Field | Backend Field | Action |
|---|---|---|
| `fullName` | `first_name` + `last_name` | Split on last space |
| `studentId` | `roll_number` | Rename |
| `email` | `email` | ✅ Matches |
| `contactNumber` | `contact_number` | ✅ Matches |
| `department` | `department` | ✅ Matches |
| `batch` | `year_batch` | Rename |
| `semester` | `semester` (int) | Cast to integer |
| `section` | `section` | ✅ Matches |
| `gender` | `gender` | ✅ Matches |
| `course` | `course` | ✅ Matches |
| `capturedImage` | `face_encoding` | ⚠️ See Task 3.3 |

**Changes to `Register.jsx`**:
```javascript
const handleSubmit = async () => {
  if (!validateForm() || !isFaceCaptured) return;

  // Split fullName into first_name + last_name
  const nameParts = formData.fullName.trim().split(' ');
  const firstName = nameParts[0];
  const lastName = nameParts.slice(1).join(' ') || nameParts[0];

  const payload = {
    first_name: firstName,
    last_name: lastName,
    email: formData.email,
    roll_number: formData.studentId,
    contact_number: formData.contactNumber || null,
    department: formData.department,
    course: formData.course,
    year_batch: formData.batch,
    semester: parseInt(formData.semester),
    section: formData.section || null,
    gender: formData.gender,
    // face_encoding will be handled by the Backend registration endpoint
  };

  try {
    const response = await createStudent(payload);
    const studentId = extractData(response).id;

    // Step 2: Upload face images to create AI dataset
    await uploadFaceImages(studentId, capturedImage);

    setAlert({ variant: 'success', message: 'Registration Successful!' });
    handleReset();
  } catch (error) {
    setAlert({ variant: 'error', message: extractErrorMessage(error) });
  }
};
```

---

### Task 3.2 — Add Backend Registration Endpoint with Face Image Support

**New endpoint**: `POST /api/v1/students/{student_id}/register-face`

**File**: `backend/Backend/app/routes/student.py`

```python
import base64
import os
from pathlib import Path
from fastapi import UploadFile, File

AI_DATASET_DIR = os.getenv("AI_DATASET_DIR", "/path/to/ai-module/AI_Module/dataset")

@router.post("/{student_id}/register-face", status_code=status.HTTP_201_CREATED)
def register_face(
    student_id: int,
    payload: dict,  # { "images": ["base64_image_1", ...] }
    db: Session = Depends(get_db),
):
    """
    Receive base64 face images from Frontend, save to AI Module dataset folder,
    then trigger encoding generation.
    """
    student = student_service.get_student(db, student_id)
    
    # Create AI dataset folder: {id}_{firstname}
    folder_name = f"{student.id}_{student.first_name}"
    folder_path = Path(AI_DATASET_DIR) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Save images
    images = payload.get("images", [])
    for idx, img_base64 in enumerate(images):
        # Strip data:image/jpeg;base64, prefix if present
        if "," in img_base64:
            img_base64 = img_base64.split(",")[1]
        
        img_bytes = base64.b64decode(img_base64)
        img_path = folder_path / f"sample_{idx + 1:02d}.jpg"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
    
    return success_response(
        data={"student_id": student.id, "images_saved": len(images), "folder": str(folder_path)},
        message="Face images registered successfully",
        status_code=201,
    )
```

---

### Task 3.3 — Update Frontend WebcamFeed for Multi-Capture

Currently, WebcamFeed captures a **single** image. For reliable AI recognition, we need **multiple face samples** (matching AI Module's `CAPTURE_SAMPLE_COUNT = 20`).

**Option A (Simpler)**: Capture 5 images at intervals from the webcam feed and send all to Backend.

**Option B (Full)**: Match AI Module's 20-sample capture with quality validation.

**Recommended: Option A** for initial integration. Enhance later.

**Add to `src/services/api.js`**:
```javascript
export const registerFace = (studentId, images) =>
  api.post(`/api/v1/students/${studentId}/register-face`, { images });
```

**Add multi-capture logic to WebcamFeed** or Register page:
```javascript
const captureMultipleFrames = async (count = 5, intervalMs = 500) => {
  const frames = [];
  for (let i = 0; i < count; i++) {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) frames.push(imageSrc);
    await new Promise(r => setTimeout(r, intervalMs));
  }
  return frames;
};
```

---

### Task 3.4 — Backend Config for AI Dataset Path

Add to `backend/Backend/app/config.py`:
```python
# AI Module Integration
AI_DATASET_DIR = os.getenv("AI_DATASET_DIR", "")
```

Add to `backend/Backend/.env`:
```env
AI_DATASET_DIR=/absolute/path/to/ai-module/AI_Module/dataset
```

---

### Task 3.5 — Trigger Encoding Regeneration

After new face images are saved, the AI Module needs to regenerate its `encodings.pickle` file.

**Option A**: Run `encode_faces.py` manually after registration.
**Option B**: Backend calls a subprocess or an API on the AI Module.
**Option C**: AI Module auto-detects new files (Phase 7 `EncodingCache.reload_if_changed()`).

**Recommended**: Option C is already partially built in Phase 7. The `EncodingCache` already checks for file modifications every 30 seconds. After registration:
1. Frontend registers student → Backend saves images to dataset folder
2. Admin/operator runs `python encode_faces.py` once
3. AI Module's `EncodingCache` auto-reloads within 30 seconds

For a **smoother flow**, add a Backend endpoint that triggers encoding:

```python
@router.post("/{student_id}/encode", status_code=200)
def trigger_encoding(student_id: int, db: Session = Depends(get_db)):
    """Trigger AI Module encoding regeneration."""
    import subprocess
    result = subprocess.run(
        ["python", "encode_faces.py"],
        cwd=AI_MODULE_DIR,
        capture_output=True, text=True, timeout=120
    )
    return success(data={"stdout": result.stdout, "returncode": result.returncode})
```

---

## 🔄 Complete Registration Flow (After Integration)

```
1. Student opens /register page
2. Webcam opens → Student captures face (5 frames captured)
3. Student fills form → clicks "Register"
4. Frontend calls POST /api/v1/students/ with student data
5. Backend creates Student record in MySQL → returns student.id
6. Frontend calls POST /api/v1/students/{id}/register-face with base64 images
7. Backend saves images to ai-module/AI_Module/dataset/{id}_{name}/
8. (Optional) Backend triggers encode_faces.py
9. AI Module's EncodingCache detects changes → reloads encodings
10. Student is now recognizable by the AI recognition system
```

---

## ✅ Verification Checklist
- [ ] Frontend form fields map correctly to Backend `StudentCreate` schema
- [ ] Student created in MySQL with correct data
- [ ] Face images saved to `ai-module/AI_Module/dataset/{id}_{name}/`
- [ ] Running `encode_faces.py` includes the new student
- [ ] AI recognition system detects the newly registered student

---

## 📁 Files Changed
| File | Action |
|---|---|
| `frontend/Frontend/src/pages/Register.jsx` | **MODIFY** — fix form field mapping |
| `frontend/Frontend/src/services/api.js` | **MODIFY** — add `registerFace()` |
| `backend/Backend/app/routes/student.py` | **MODIFY** — add `/register-face` endpoint |
| `backend/Backend/app/config.py` | **MODIFY** — add `AI_DATASET_DIR` |
| `backend/Backend/.env` | **MODIFY** — add `AI_DATASET_DIR` path |
