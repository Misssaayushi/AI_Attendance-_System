"""Attendance service layer (Phase 5 Step 1 architecture scaffold)."""

from __future__ import annotations

import math
from datetime import date, datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.exceptions import (
    AttendanceNotFoundException,
    AttendanceVerificationException,
    DuplicateAttendanceException,
    StudentNotFoundException,
)
from app.exports import normalize_export_row
from app.repositories import attendance_repository
from app.schemas.attendance import AttendanceMarkRequest, AttendanceSummaryResponse
from app.utils.logger import logger


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
    records, total = attendance_repository.list_attendance(
        db,
        page=page,
        page_size=page_size,
        student_id=student_id,
        department=department,
        search=search,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )
    logger.info(
        "event=attendance_listed page=%s page_size=%s total=%s student_id=%s department=%s status=%s from_date=%s to_date=%s",
        page,
        page_size,
        total,
        student_id,
        department,
        status,
        from_date,
        to_date,
    )
    return records, total


def mark_attendance(
    db: Session,
    payload: AttendanceMarkRequest,
    *,
    min_confidence: float = 0.6,
) -> models.Attendance:
    """
    Step 3: Attendance verification workflow.
    Step 4: Duplicate prevention.
    """
    student = db.query(models.Student).filter(models.Student.id == payload.student_id).first()
    if not student:
        logger.warning("event=attendance_mark_rejected reason=student_not_found student_id=%s", payload.student_id)
        raise StudentNotFoundException("Student not found for attendance marking")

    if payload.confidence_score is not None and payload.confidence_score < min_confidence:
        logger.warning(
            "event=attendance_mark_rejected reason=low_confidence student_id=%s confidence=%s threshold=%s",
            payload.student_id,
            payload.confidence_score,
            min_confidence,
        )
        raise AttendanceVerificationException(
            f"Recognition confidence below threshold ({payload.confidence_score:.2f} < {min_confidence:.2f})"
        )

    now_utc = datetime.now(timezone.utc)
    attendance_date = payload.attendance_date or now_utc.date()
    attendance_time = payload.attendance_time or now_utc.time().replace(microsecond=0)

    existing = attendance_repository.get_by_student_and_date(
        db,
        student_id=payload.student_id,
        attendance_date=attendance_date,
    )
    if existing:
        logger.warning(
            "event=attendance_mark_rejected reason=duplicate student_id=%s attendance_date=%s",
            payload.student_id,
            attendance_date,
        )
        raise DuplicateAttendanceException("Attendance already marked for this student on this date")

    try:
        record = attendance_repository.create(
            db,
            student_id=payload.student_id,
            attendance_date=attendance_date,
            attendance_time=attendance_time,
            status=payload.status.value,
        )
        logger.info(
            "event=attendance_marked attendance_id=%s student_id=%s attendance_date=%s status=%s",
            record.id,
            record.student_id,
            record.date,
            record.status,
        )
        return record
    except IntegrityError as exc:
        db.rollback()
        logger.warning(
            "event=attendance_mark_rejected reason=db_duplicate student_id=%s attendance_date=%s",
            payload.student_id,
            attendance_date,
        )
        raise DuplicateAttendanceException("Duplicate attendance rejected at database level") from exc


def get_attendance_by_id(db: Session, attendance_id: int) -> models.Attendance:
    record = attendance_repository.get_by_id(db, attendance_id)
    if not record:
        logger.warning("event=attendance_not_found attendance_id=%s", attendance_id)
        raise AttendanceNotFoundException("Attendance record not found")
    return record


def get_daily_summary(db: Session, *, target_date: Optional[date] = None) -> AttendanceSummaryResponse:
    summary_date = target_date or datetime.now(timezone.utc).date()
    counts = attendance_repository.get_daily_counts(db, target_date=summary_date)
    total_students = db.query(models.Student).count()
    present_count = counts["present"]
    absent_count = counts["absent"]
    late_count = counts["late"]
    percentage = 0.0
    if total_students > 0:
        percentage = round((present_count / total_students) * 100, 2)
    summary = AttendanceSummaryResponse(
        date=summary_date.isoformat(),
        total_students=total_students,
        present_count=present_count,
        absent_count=absent_count,
        late_count=late_count,
        attendance_percentage=percentage,
    )
    logger.info(
        "event=attendance_daily_summary date=%s total_students=%s present=%s absent=%s late=%s percentage=%s",
        summary.date,
        summary.total_students,
        summary.present_count,
        summary.absent_count,
        summary.late_count,
        summary.attendance_percentage,
    )
    return summary


def build_paginated_response(items: list[models.Attendance], total: int, page: int, page_size: int) -> dict:
    pages = math.ceil(total / page_size) if total > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


def build_export_preview(
    db: Session,
    *,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    student_id: Optional[int] = None,
) -> list[dict]:
    """
    Step 10 hook:
    Returns normalized attendance rows that future Excel writers can consume directly.
    """
    exported_at = datetime.now(timezone.utc)
    records = attendance_repository.list_for_export(
        db,
        from_date=from_date,
        to_date=to_date,
        student_id=student_id,
    )
    rows = [normalize_export_row(record, exported_at=exported_at).model_dump(mode="json") for record in records]
    logger.info(
        "event=attendance_export_preview rows=%s from_date=%s to_date=%s student_id=%s",
        len(rows),
        from_date,
        to_date,
        student_id,
    )
    return rows
