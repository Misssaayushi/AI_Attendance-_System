"""Attendance export preparation utilities (Phase 5 Step 10)."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel


class AttendanceExportRow(BaseModel):
    """Stable row contract for future Excel/report writers."""

    attendance_id: int
    attendance_date: date
    attendance_time: time
    status: str
    student_id: int
    roll_number: Optional[str] = None
    student_name: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    exported_at: datetime


def normalize_export_row(record, *, exported_at: datetime) -> AttendanceExportRow:
    student = getattr(record, "student", None)
    return AttendanceExportRow(
        attendance_id=record.id,
        attendance_date=record.date,
        attendance_time=record.time,
        status=record.status,
        student_id=record.student_id,
        roll_number=getattr(student, "roll_number", None),
        student_name=getattr(student, "full_name", None),
        department=getattr(student, "department", None),
        course=getattr(student, "course", None),
        semester=getattr(student, "semester", None),
        section=getattr(student, "section", None),
        exported_at=exported_at,
    )

