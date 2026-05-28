from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app import models
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
    student = student_repository.get_by_id(db, student_id)
    if not student:
        raise StudentNotFoundException("Student not found")
    student_repository.delete(db, student)
