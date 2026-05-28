from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.schemas import student as student_schema

def get_by_id(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_by_roll(db: Session, roll_number: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.roll_number == roll_number).first()

def get_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email_address == email).first()

def list_students(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> Tuple[List[models.Student], int]:
    query = db.query(models.Student)
    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            models.Student.first_name.ilike(pattern)
            | models.Student.last_name.ilike(pattern)
            | models.Student.roll_number.ilike(pattern)
        )
    total = query.with_entities(func.count()).scalar()
    records = query.offset(skip).limit(limit).all()
    return records, total

def create(db: Session, payload: student_schema.StudentCreate) -> models.Student:
    student = models.Student(
        first_name=payload.first_name,
        last_name=payload.last_name,
        roll_number=payload.roll_number,
        email_address=payload.email,
        contact_number=payload.contact_number,
        department=payload.department,
        course=payload.course,
        year_batch=payload.year_batch,
        semester=payload.semester,
        section=payload.section,
        gender=payload.gender,
        face_encoding=None if payload.face_encoding is None else str(payload.face_encoding),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def update(db: Session, *, student: models.Student, payload: student_schema.StudentUpdate) -> models.Student:
    for attr in [
        "first_name",
        "last_name",
        "email",
        "roll_number",
        "contact_number",
        "department",
        "course",
        "year_batch",
        "semester",
        "section",
        "gender",
        "face_encoding",
    ]:
        value = getattr(payload, attr, None)
        if value is not None:
            model_attr = "email_address" if attr == "email" else attr
            setattr(student, model_attr, value)
    db.commit()
    db.refresh(student)
    return student

def delete(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()
