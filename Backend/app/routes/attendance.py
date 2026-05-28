from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.middleware.auth_deps import get_current_admin
from app.schemas import attendance as attendance_schema
from app.services import attendance_service
from app.utils.logger import logger
from app.utils.response import success, success_response

router = APIRouter(dependencies=[Depends(get_current_admin)])


def _serialize_record(record) -> dict:
    return attendance_schema.AttendanceRecordResponse(
        id=record.id,
        student_id=record.student_id,
        student_name=record.student.full_name if record.student else None,
        roll_number=record.student.roll_number if record.student else None,
        attendance_date=record.date,
        attendance_time=record.time,
        status=record.status,
        confidence_score=None,
        source=None,
        created_at=None,
    ).model_dump(mode="json")


@router.post("/mark", status_code=status.HTTP_201_CREATED)
def mark_attendance(
    payload: attendance_schema.AttendanceMarkRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_mark_request student_id=%s status=%s confidence=%s source=%s",
        payload.student_id,
        payload.status.value,
        payload.confidence_score,
        payload.source,
    )
    record = attendance_service.mark_attendance(db, payload)
    response = attendance_schema.AttendanceMarkResponse(
        id=record.id,
        student_id=record.student_id,
        attendance_date=record.date,
        attendance_time=record.time,
        status=record.status,
        confidence_score=payload.confidence_score,
        source=payload.source,
        message="Attendance marked successfully",
    ).model_dump(mode="json")
    return success_response(data=response, message="Attendance marked successfully", status_code=201)


@router.get("/")
def list_attendance(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: int | None = Query(default=None, gt=0),
    department: str | None = None,
    search: str | None = None,
    status: attendance_schema.AttendanceStatus | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_list_request page=%s page_size=%s student_id=%s department=%s status=%s from_date=%s to_date=%s search=%s",
        page,
        page_size,
        student_id,
        department,
        status.value if status else None,
        from_date,
        to_date,
        search,
    )
    records, total = attendance_service.list_attendance(
        db,
        page=page,
        page_size=page_size,
        student_id=student_id,
        department=department,
        search=search,
        status=status.value if status else None,
        from_date=from_date,
        to_date=to_date,
    )
    serialized_items = [_serialize_record(r) for r in records]
    response = attendance_service.build_paginated_response(serialized_items, total, page, page_size)
    return success(data=response, message="Attendance records retrieved successfully")


@router.get("/summary/daily")
def daily_summary(
    target_date: date | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=attendance_daily_summary_request target_date=%s", target_date)
    summary = attendance_service.get_daily_summary(db, target_date=target_date)
    return success(data=summary.model_dump(mode="json"), message="Daily attendance summary retrieved successfully")


@router.get("/student/{student_id}")
def get_student_attendance(
    student_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    logger.info(
        "event=student_attendance_request student_id=%s page=%s page_size=%s from_date=%s to_date=%s",
        student_id,
        page,
        page_size,
        from_date,
        to_date,
    )
    records, total = attendance_service.list_attendance(
        db,
        page=page,
        page_size=page_size,
        student_id=student_id,
        from_date=from_date,
        to_date=to_date,
    )
    serialized_items = [_serialize_record(r) for r in records]
    response = attendance_service.build_paginated_response(serialized_items, total, page, page_size)
    return success(data=response, message="Student attendance records retrieved successfully")


@router.get("/export/preview")
def export_preview(
    from_date: date | None = None,
    to_date: date | None = None,
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_preview_request from_date=%s to_date=%s student_id=%s",
        from_date,
        to_date,
        student_id,
    )
    rows = attendance_service.build_export_preview(
        db,
        from_date=from_date,
        to_date=to_date,
        student_id=student_id,
    )
    return success(data={"rows": rows, "count": len(rows)}, message="Attendance export preview generated")


@router.get("/{attendance_id}")
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    logger.info("event=attendance_get_request attendance_id=%s", attendance_id)
    record = attendance_service.get_attendance_by_id(db, attendance_id)
    return success(data=_serialize_record(record), message="Attendance record retrieved successfully")
