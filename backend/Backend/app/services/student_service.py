from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime
from zoneinfo import ZoneInfo

from app import models
from app.config import settings
from app.repositories import student_repository
from app.schemas import student as student_schema
from app.utils.pagination import paginate, apply_student_filters
from app.exceptions import (
    StudentNotFoundException,
    DuplicateRollNumberException,
    DuplicateEmailException,
)

def create_student(db: Session, payload: student_schema.StudentCreate) -> models.Student:
    """Create a new student record after performing uniqueness checks."""
    # Check email uniqueness
    if student_repository.get_by_email(db, payload.email):
        raise DuplicateEmailException("Email address already registered")
        
    # Check roll number uniqueness
    if student_repository.get_by_roll(db, payload.roll_number):
        raise DuplicateRollNumberException("Roll number already registered")
        
    return student_repository.create(db, payload)

def get_student(db: Session, student_id: int) -> models.Student:
    """Retrieve a student record by ID. Raise StudentNotFoundException if not found."""
    student = student_repository.get_by_id(db, student_id)
    if not student:
        raise StudentNotFoundException("Student not found")
    return student

def list_students(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    department: Optional[str] = None,
    year: Optional[int] = None,
) -> Tuple[List[models.Student], int]:
    """Retrieve students list with pagination and optional filtering."""
    query = db.query(models.Student)
    query = apply_student_filters(query, search=search, department=department, year=year)
    return paginate(query, page=page, page_size=page_size)

def update_student(
    db: Session,
    student_id: int,
    payload: student_schema.StudentUpdate,
) -> models.Student:
    """Update an existing student record after performing uniqueness checks."""
    student = student_repository.get_by_id(db, student_id)
    if not student:
        raise StudentNotFoundException("Student not found")
        
    # If email is being updated, verify uniqueness
    if payload.email is not None and payload.email != student.email_address:
        existing = student_repository.get_by_email(db, payload.email)
        if existing and existing.id != student_id:
            raise DuplicateEmailException("Email address already registered")
            
    # If roll number is being updated, verify uniqueness
    if payload.roll_number is not None and payload.roll_number != student.roll_number:
        existing = student_repository.get_by_roll(db, payload.roll_number)
        if existing and existing.id != student_id:
            raise DuplicateRollNumberException("Roll number already registered")
            
    return student_repository.update(db, student=student, payload=payload)

def delete_student(db: Session, student_id: int) -> None:
    """Delete a student record by ID. Raise StudentNotFoundException if not found."""
    import shutil
    import subprocess
    import sys
    from pathlib import Path
    
    student = student_repository.get_by_id(db, student_id)
    if not student:
        raise StudentNotFoundException("Student not found")
        
    # Get student info for directory deletion before removing from DB
    student_id_val = student.id
    
    # 1. Delete student from database
    student_repository.delete(db, student)
    
    # 2. Clean up AI dataset directories.
    # Use the ID prefix so admin name edits do not leave stale face folders.
    dataset_root = Path(settings.AI_DATASET_DIR)
    dataset_folders = []
    if dataset_root.exists():
        dataset_folders = [
            path for path in dataset_root.iterdir()
            if path.is_dir() and (path.name == str(student_id_val) or path.name.startswith(f"{student_id_val}_"))
        ]

    for dataset_folder in dataset_folders:
        try:
            shutil.rmtree(dataset_folder)
        except Exception as e:
            # Log it but don't fail the operation
            print(f"Failed to delete dataset directory: {e}")

    # 3. Clean up individual pickle encodings.
    encodings_root = Path(settings.AI_MODULE_DIR) / "encodings"
    pkl_files = []
    if encodings_root.exists():
        pkl_files = [
            path for path in encodings_root.iterdir()
            if path.is_file()
            and path.suffix == ".pkl"
            and (path.stem == str(student_id_val) or path.stem.startswith(f"{student_id_val}_"))
        ]

    for pkl_file in pkl_files:
        try:
            pkl_file.unlink()
        except Exception as e:
            print(f"Failed to delete individual encoding file: {e}")

    try:
        from app.routes.attendance import _dataset_cache

        for cache_key in list(_dataset_cache.keys()):
            if cache_key == str(student_id_val) or cache_key.startswith(f"{student_id_val}_"):
                del _dataset_cache[cache_key]
    except Exception:
        pass
            
    # 4. Rebuild the consolidated encodings.pickle file
    try:
        import os
        ai_python = os.path.join(settings.AI_MODULE_DIR, "venv", "bin", "python")
        if not os.path.exists(ai_python):
            ai_python = sys.executable
        subprocess.run(
            [ai_python, "encode_faces.py"],
            cwd=settings.AI_MODULE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
    except Exception as e:
        print(f"Failed to trigger encode_faces.py: {e}")
        
    # 5. Reload the backend's in-memory cache immediately
    try:
        if settings.AI_MODULE_DIR not in sys.path:
            sys.path.append(settings.AI_MODULE_DIR)
        from optimization import EncodingCache
        from config import ENCODING_FILE
        
        cache = EncodingCache.get_instance()
        cache.load(ENCODING_FILE)
    except Exception as e:
        print(f"Failed to reload backend AI cache: {e}")

def enrich_students_with_attendance_stats(db: Session, students: List[models.Student], date_str: str = None) -> List[dict]:
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.now(ZoneInfo(settings.ATTENDANCE_TIMEZONE)).date()
    else:
        target_date = datetime.now(ZoneInfo(settings.ATTENDANCE_TIMEZONE)).date()
        
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return []
        
    stats_query = db.query(
        models.Attendance.student_id,
        func.count(models.Attendance.id).label('total'),
        func.sum(case((models.Attendance.status.in_(['Present', 'Late']), 1), else_=0)).label('attended')
    ).filter(
        models.Attendance.student_id.in_(student_ids)
    ).group_by(models.Attendance.student_id).all()
    
    stats_map = {row.student_id: (row.total, row.attended) for row in stats_query}
    
    today_query = db.query(
        models.Attendance.student_id,
        models.Attendance.id.label('attendance_id'),
        models.Attendance.status,
        models.Attendance.time
    ).filter(
        models.Attendance.student_id.in_(student_ids),
        models.Attendance.date == target_date
    ).all()
    
    today_map = {row.student_id: row for row in today_query}
    
    enriched = []
    for s in students:
        s_dict = student_schema.StudentResponse.from_orm(s).dict()
        total, attended = stats_map.get(s.id, (0, 0))
        attended_val = int(attended) if attended else 0
        total_val = int(total) if total else 0
        rate = (attended_val / total_val * 100) if total_val > 0 else 100.0
        
        today_record = today_map.get(s.id)
        
        s_dict['attendance_rate'] = round(rate, 1)
        s_dict['status'] = today_record.status if today_record else None
        s_dict['arrival_time'] = str(today_record.time) if today_record and today_record.time else None
        s_dict['attendance_id'] = today_record.attendance_id if today_record else None
        
        enriched.append(s_dict)
        
    return enriched
