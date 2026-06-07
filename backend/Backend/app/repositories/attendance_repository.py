"""Attendance repository layer (Phase 5 Step 1 architecture scaffold)."""

from __future__ import annotations

from datetime import date, time
from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Query, Session, joinedload

from app import models


def build_attendance_query(
    db: Session,
    *,
    student_id: Optional[int] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Query:
    query = db.query(models.Attendance).options(joinedload(models.Attendance.student))
    if student_id is not None:
        query = query.filter(models.Attendance.student_id == student_id)
    if department is not None or search is not None:
        query = query.join(models.Student, models.Student.id == models.Attendance.student_id)
    if department is not None:
        query = query.filter(models.Student.department == department)
    if search is not None:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            models.Student.first_name.ilike(pattern)
            | models.Student.last_name.ilike(pattern)
            | models.Student.roll_number.ilike(pattern)
        )
    if status is not None:
        query = query.filter(models.Attendance.status == status)
    if from_date is not None:
        query = query.filter(models.Attendance.date >= from_date)
    if to_date is not None:
        query = query.filter(models.Attendance.date <= to_date)
    return query


def list_attendance(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    student_id: Optional[int] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Tuple[list[models.Attendance], int]:
    query = build_attendance_query(
        db,
        student_id=student_id,
        department=department,
        search=search,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )
    total = query.order_by(None).count()
    offset = (page - 1) * page_size
    items = query.order_by(models.Attendance.date.desc(), models.Attendance.time.desc()).offset(offset).limit(page_size).all()
    return items, total


def get_by_id(db: Session, attendance_id: int) -> Optional[models.Attendance]:
    return (
        db.query(models.Attendance)
        .options(joinedload(models.Attendance.student))
        .filter(models.Attendance.id == attendance_id)
        .first()
    )


def get_by_student_and_date(
    db: Session,
    *,
    student_id: int,
    attendance_date: date,
) -> Optional[models.Attendance]:
    return (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == student_id,
            models.Attendance.date == attendance_date,
        )
        .first()
    )


def create(
    db: Session,
    *,
    student_id: int,
    attendance_date: date,
    attendance_time: time,
    status: str,
) -> models.Attendance:
    record = models.Attendance(
        student_id=student_id,
        date=attendance_date,
        time=attendance_time,
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_daily_counts(db: Session, *, target_date: date) -> dict:
    rows = (
        db.query(models.Attendance.status, func.count(models.Attendance.id))
        .filter(models.Attendance.date == target_date)
        .group_by(models.Attendance.status)
        .all()
    )
    counts = {status: count for status, count in rows}
    return {
        "present": counts.get("Present", 0),
        "absent": counts.get("Absent", 0),
        "late": counts.get("Late", 0),
    }


def list_for_export(
    db: Session,
    *,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    student_id: Optional[int] = None,
) -> list[models.Attendance]:
    query = build_attendance_query(
        db,
        student_id=student_id,
        from_date=from_date,
        to_date=to_date,
    )
    return query.order_by(models.Attendance.date.asc(), models.Attendance.time.asc()).all()
