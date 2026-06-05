"""Pydantic schemas for Attendance Management API (Phase 5 Step 2)."""

from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationInfo, confloat, field_validator


class AIAttendancePayload(BaseModel):
    """Schema for incoming AI Module attendance events."""
    student_id: str  # AI sends string, we convert to int
    name: str
    confidence: float  # 0-100 scale
    timestamp: str  # ISO-8601
    status: str = "Present"

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v):
        try:
            int_id = int(v)
            if int_id <= 0:
                raise ValueError
            return v
        except (ValueError, TypeError):
            raise ValueError("student_id must be a positive integer string")


class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"


class AttendanceMarkRequest(BaseModel):
    student_id: int = Field(..., gt=0)
    attendance_date: Optional[date] = None
    attendance_time: Optional[time] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT
    confidence_score: Optional[confloat(ge=0.0, le=1.0)] = None
    source: Optional[str] = "ai_recognition"


class AttendanceMarkResponse(BaseModel):
    id: int
    student_id: int
    attendance_date: date
    attendance_time: time
    status: AttendanceStatus
    confidence_score: Optional[float] = None
    source: Optional[str] = None
    message: str = "Attendance marked successfully"


class AttendanceRecordResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    attendance_date: date
    attendance_time: time
    status: AttendanceStatus
    confidence_score: Optional[float] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None


class AttendanceFilterParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    student_id: Optional[int] = Field(None, gt=0)
    department: Optional[str] = None
    status: Optional[AttendanceStatus] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    search: Optional[str] = None

    @field_validator("to_date")
    @classmethod
    def validate_date_range(cls, v, info: ValidationInfo):
        from_date = info.data.get("from_date")
        if from_date and v and v < from_date:
            raise ValueError("to_date must be greater than or equal to from_date")
        return v


class AttendanceListResponse(BaseModel):
    items: List[AttendanceRecordResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AttendanceSummaryResponse(BaseModel):
    date: Optional[str] = None
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: float
