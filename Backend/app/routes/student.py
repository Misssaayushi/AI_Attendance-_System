from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import math
import base64
import subprocess
from pathlib import Path

from app.database.connection import get_db
from app.config import settings
from app.schemas import student as student_schema
from app.services import student_service
from app.middleware.auth_deps import get_current_admin
from app.utils.request_validation import normalize_page_size, normalize_search
from app.utils.response import success, success_response

# Remove global admin protection so registration can be public
router = APIRouter()

# ---------------------------------------------------------------------
# List students with optional pagination & filtering
# ---------------------------------------------------------------------
@router.get("/")
def list_students(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    department: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    page_size = normalize_page_size(page_size)
    search = normalize_search(search)
    students, total = student_service.list_students(
        db, page=page, page_size=page_size, search=search, department=department, year=year
    )
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    items_serialized = student_service.enrich_students_with_attendance_stats(db, students)
    response_data = {
        "items": items_serialized,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
    return success(data=response_data, message="Students retrieved successfully")

# ---------------------------------------------------------------------
# Retrieve a single student by ID
# ---------------------------------------------------------------------
@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    student = student_service.get_student(db, student_id)
    student_serialized = student_schema.StudentResponse.from_orm(student).dict()
    return success(data=student_serialized, message="Student retrieved successfully")

# ---------------------------------------------------------------------
# Create a new student
# ---------------------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_student(payload: student_schema.StudentCreate, db: Session = Depends(get_db)):
    student = student_service.create_student(db, payload)
    student_serialized = student_schema.StudentResponse.from_orm(student).dict()
    return success_response(
        data=student_serialized,
        message="Student created successfully",
        status_code=status.HTTP_201_CREATED,
    )

# ---------------------------------------------------------------------
# Update an existing student
# ---------------------------------------------------------------------
@router.put("/{student_id}")
def update_student(
    student_id: int,
    payload: student_schema.StudentUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    student = student_service.update_student(db, student_id, payload)
    student_serialized = student_schema.StudentResponse.from_orm(student).dict()
    return success(data=student_serialized, message="Student updated successfully")

# ---------------------------------------------------------------------
# Delete a student
# ---------------------------------------------------------------------
@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    student_service.delete_student(db, student_id)
    return success(data=None, message="Student deleted successfully")

# ---------------------------------------------------------------------
# Register face images for a student
# ---------------------------------------------------------------------
@router.post("/{student_id}/register-face", status_code=status.HTTP_201_CREATED)
def register_face(
    student_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    student = student_service.get_student(db, student_id)
    
    # Create AI dataset folder: {id}_{firstname}
    folder_name = f"{student.id}_{student.first_name}"
    folder_path = Path(settings.AI_DATASET_DIR) / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    
    images = payload.get("images", [])
    if not isinstance(images, list) or not images:
        raise HTTPException(status_code=400, detail="At least one face image is required")

    for idx, img_base64 in enumerate(images):
        if "," in img_base64:
            img_base64 = img_base64.split(",")[1]

        try:
            img_bytes = base64.b64decode(img_base64, validate=True)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid image data at position {idx + 1}") from exc

        img_path = folder_path / f"sample_{idx + 1:02d}.jpg"
        with open(img_path, "wb") as f:
            f.write(img_bytes)

    try:
        from app.routes.attendance import _dataset_cache

        _dataset_cache.pop(folder_name, None)
    except Exception:
        pass
            
    return success_response(
        data={"student_id": student.id, "images_saved": len(images), "folder": str(folder_path)},
        message="Face images registered successfully",
        status_code=status.HTTP_201_CREATED,
    )

# ---------------------------------------------------------------------
# Trigger face encoding process
# ---------------------------------------------------------------------
@router.post("/{student_id}/encode", status_code=status.HTTP_200_OK)
def trigger_encoding(student_id: int, db: Session = Depends(get_db)):
    import pickle
    import json
    
    student = student_service.get_student(db, student_id) # Verify student exists
    try:
        import os
        ai_python = os.path.join(settings.AI_MODULE_DIR, "venv", "bin", "python")
        if not os.path.exists(ai_python):
            import sys
            ai_python = sys.executable
        result = subprocess.run(
            [ai_python, "encode_faces.py"],
            cwd=settings.AI_MODULE_DIR,
            capture_output=True, 
            text=True, 
            timeout=120
        )
        if result.returncode != 0:
            return success_response(data={"error": result.stderr}, message="Encoding failed", status_code=500)
            
        # Parse the individual encoding file generated
        folder_name = f"{student.id}_{student.first_name}"
        pkl_path = Path(settings.AI_MODULE_DIR) / "encodings" / f"{folder_name}.pkl"
        
        if pkl_path.exists():
            with open(pkl_path, "rb") as f:
                encodings = pickle.load(f)
            
            if encodings and len(encodings) > 0:
                # Average encodings if multiple or just take first. The individual pkl is a list of encodings.
                # Average them:
                import numpy as np
                avg_encoding = np.mean(encodings, axis=0).tolist()
                
                # Save to DB
                student_service.update_student(
                    db, 
                    student_id, 
                    student_schema.StudentUpdate(face_encoding=avg_encoding)
                )
                
        return success(data={"stdout": result.stdout, "returncode": result.returncode}, message="Encoding triggered successfully and saved to DB")
    except Exception as e:
        return success_response(data={"error": str(e)}, message="Failed to trigger encoding", status_code=500)

# ---------------------------------------------------------------------
# Rebuild encodings.pickle from database
# ---------------------------------------------------------------------
@router.post("/rebuild-encodings", status_code=status.HTTP_200_OK)
def rebuild_encodings(db: Session = Depends(get_db)):
    import pickle
    import json
    import sys
    from app import models
    
    students = db.query(models.Student).filter(models.Student.face_encoding.isnot(None)).all()
    
    known_encodings = []
    known_names = []
    
    for s in students:
        try:
            encoding = json.loads(s.face_encoding)
            if isinstance(encoding, list) and len(encoding) == 128:
                folder_name = f"{s.id}_{s.first_name}"
                known_encodings.append(encoding)
                known_names.append(folder_name)
        except Exception:
            continue
            
    # Set the path to the correct consolidated cache file
    pkl_path = Path(settings.AI_MODULE_DIR) / "encodings" / "encodings.pickle"
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not known_encodings:
        # If no encodings exist, delete or clean the file
        if pkl_path.exists():
            try:
                pkl_path.unlink()
            except Exception:
                pass
    else:
        data = {"encodings": known_encodings, "names": known_names}
        with open(pkl_path, "wb") as f:
            pickle.dump(data, f)
            
    # Trigger cache reload in backend
    try:
        if settings.AI_MODULE_DIR not in sys.path:
            sys.path.append(settings.AI_MODULE_DIR)
        from optimization import EncodingCache
        from config import ENCODING_FILE
        
        cache = EncodingCache.get_instance()
        cache.load(ENCODING_FILE)
    except Exception as e:
        print(f"Failed to reload backend AI cache in rebuild: {e}")
        
    return success(
        data={"rebuilt_count": len(known_encodings), "file_path": str(pkl_path)}, 
        message="Encodings rebuilt successfully from database"
    )
