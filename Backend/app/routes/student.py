from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import math

from app.database.connection import get_db
from app.schemas import student as student_schema
from app.services import student_service
from app.middleware.auth_deps import get_current_admin
from app.utils.response import success

# Protect all student routes with admin authentication
router = APIRouter(dependencies=[Depends(get_current_admin)])

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
):
    students, total = student_service.list_students(
        db, page=page, page_size=page_size, search=search, department=department, year=year
    )
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    items_serialized = [student_schema.StudentResponse.from_orm(s).dict() for s in students]
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
def get_student(student_id: int, db: Session = Depends(get_db)):
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
    return success(data=student_serialized, message="Student created successfully")

# ---------------------------------------------------------------------
# Update an existing student
# ---------------------------------------------------------------------
@router.put("/{student_id}")
def update_student(
    student_id: int,
    payload: student_schema.StudentUpdate,
    db: Session = Depends(get_db),
):
    student = student_service.update_student(db, student_id, payload)
    student_serialized = student_schema.StudentResponse.from_orm(student).dict()
    return success(data=student_serialized, message="Student updated successfully")

# ---------------------------------------------------------------------
# Delete a student
# ---------------------------------------------------------------------
@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student_service.delete_student(db, student_id)
    return success(data=None, message="Student deleted successfully")

