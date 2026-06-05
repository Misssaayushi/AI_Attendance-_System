from __future__ import annotations

from datetime import date

import os
import asyncio
from fastapi import APIRouter, Depends, Query, status, Header, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.middleware.auth_deps import get_current_admin
from app.schemas import attendance as attendance_schema
from app.services import attendance_service
from app.services import auto_absent_service
from app.services import email_service
from app.services import excel_service
from app.utils.logger import logger
from app.utils.request_validation import normalize_page_size, normalize_search
from app.utils.response import success, success_response
from app.routes.websocket import broadcast_attendance_event

router = APIRouter(dependencies=[Depends(get_current_admin)])
ai_router = APIRouter()

INTERNAL_API_KEY = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")

@ai_router.post("/verify", status_code=status.HTTP_201_CREATED)
def verify_attendance_from_ai(
    payload: attendance_schema.AIAttendancePayload,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    """
    Endpoint for AI Module to send verified attendance events.
    Uses API key authentication instead of JWT.
    """
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Convert AI payload to standard attendance mark request
    mark_request = attendance_schema.AttendanceMarkRequest(
        student_id=payload.student_id,
        status=attendance_schema.AttendanceStatus(payload.status),
        confidence_score=payload.confidence / 100.0,  # Convert 0-100 -> 0.0-1.0
        source="ai_recognition",
    )
    
    record = attendance_service.mark_attendance(db, mark_request)
    
    # Broadcast real-time event to all connected Frontend clients
    event = {
        "type": "attendance_marked",
        "student_id": record.student_id,
        "student_name": record.student.full_name if record.student else payload.student_id,
        "status": record.status,
        "time": record.time.isoformat() if record.time else None,
        "confidence": payload.confidence,
    }
    background_tasks.add_task(broadcast_attendance_event, event)

    return success_response(
        data={"id": record.id, "student_id": record.student_id, "status": record.status},
        message="Attendance verified and logged",
        status_code=201,
    )



def _serialize_record(record) -> dict:
    data = attendance_schema.AttendanceRecordResponse(
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
    data["department"] = record.student.department if record.student else None
    return data


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
    page_size = normalize_page_size(page_size)
    search = normalize_search(search)
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
    page_size = normalize_page_size(page_size)
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


@router.post("/export/monthly")
def export_monthly_workbook(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    department: str | None = None,
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_monthly_request year=%s month=%s department=%s student_id=%s",
        year,
        month,
        department,
        student_id,
    )
    if department:
        data = excel_service.generate_department_monthly_report(
            db,
            year=year,
            month=month,
            department=department,
        )
        return success(data=data, message="Department monthly workbook generated")

    if student_id:
        data = excel_service.generate_student_monthly_report(
            db,
            year=year,
            month=month,
            student_id=student_id,
        )
        return success(data=data, message="Student monthly workbook generated")

    data = excel_service.generate_monthly_workbook_from_db(db, year=year, month=month)
    return success(data=data, message="Monthly workbook generated")


@router.post("/export/template")
def export_monthly_template(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
):
    logger.info("event=attendance_export_template_request year=%s month=%s", year, month)
    path = excel_service.generate_monthly_workbook_template(year=year, month=month)
    return success(data={"file_path": path, "year": year, "month": month}, message="Monthly template generated")


@router.post("/export/sync/{attendance_id}")
def sync_attendance_to_workbook(
    attendance_id: int,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_sync_request attendance_id=%s year=%s month=%s",
        attendance_id,
        year,
        month,
    )
    data = excel_service.sync_attendance_record_to_monthly_workbook(
        db,
        attendance_id=attendance_id,
        year=year,
        month=month,
    )
    return success(data=data, message="Attendance record synced to workbook")


@router.get("/automation/executions")
def scheduler_executions(
    limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    logger.info("event=scheduler_executions_list_request limit=%s", limit)
    rows = auto_absent_service.list_scheduler_executions(db, limit=limit)
    data = [
        {
            "id": row.id,
            "job_name": row.job_name,
            "run_date": row.run_date.isoformat(),
            "status": row.status,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
            "total_students": row.total_students,
            "already_marked": row.already_marked,
            "auto_absent_marked": row.auto_absent_marked,
            "duplicate_skipped": row.duplicate_skipped,
            "excel_synced": row.excel_synced,
            "attempt_count": row.attempt_count,
            "duration_ms": row.duration_ms,
            "error_message": row.error_message,
        }
        for row in rows
    ]
    return success(data={"items": data, "count": len(data)}, message="Scheduler executions retrieved successfully")


@router.get("/automation/summary")
def scheduler_summary(
    last_n: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    logger.info("event=scheduler_summary_request last_n=%s", last_n)
    summary = auto_absent_service.get_scheduler_summary(db, last_n=last_n)
    return success(data=summary, message="Scheduler summary retrieved successfully")


@router.post("/reports/email/monthly")
def send_monthly_report_email(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    recipient_group: str = Query("admin"),
    department: str | None = None,
    student_id: int | None = Query(default=None, gt=0),
    force_send: bool = Query(False),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=report_email_monthly_request year=%s month=%s recipient_group=%s department=%s student_id=%s force_send=%s",
        year,
        month,
        recipient_group,
        department,
        student_id,
        force_send,
    )
    data = email_service.send_monthly_report_email(
        db,
        year=year,
        month=month,
        recipient_group=recipient_group,
        department=department,
        student_id=student_id,
        force_send=force_send,
    )
    return success(data=data, message="Monthly report email sent successfully")


@router.post("/reports/email/daily")
def send_daily_report_email(
    target_date: date = Query(...),
    recipient_group: str = Query("admin"),
    force_send: bool = Query(False),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=report_email_daily_request date=%s recipient_group=%s force_send=%s",
        target_date,
        recipient_group,
        force_send,
    )
    data = email_service.send_daily_report_email(
        db,
        target_date=target_date,
        recipient_group=recipient_group,
        force_send=force_send,
    )
    return success(data=data, message="Daily report email sent successfully")


@router.get("/reports/email/deliveries")
def list_email_deliveries(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    logger.info("event=email_deliveries_list_request limit=%s", limit)
    rows = email_service.list_email_deliveries(db, limit=limit)
    data = [
        {
            "id": row.id,
            "report_type": row.report_type,
            "report_date": row.report_date.isoformat(),
            "recipient_group": row.recipient_group,
            "report_label": row.report_label,
            "status": row.status,
            "attempts": row.attempts,
            "recipients_count": row.recipients_count,
            "attachment_name": row.attachment_name,
            "duration_ms": row.duration_ms,
            "error_message": row.error_message,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
        }
        for row in rows
    ]
    return success(data={"items": data, "count": len(data)}, message="Email delivery history retrieved successfully")


@router.get("/reports/email/summary")
def email_delivery_summary(
    last_n: int = Query(50, ge=1, le=365),
    db: Session = Depends(get_db),
):
    logger.info("event=email_delivery_summary_request last_n=%s", last_n)
    summary = email_service.get_email_delivery_summary(db, last_n=last_n)
    return success(data=summary, message="Email delivery summary retrieved successfully")


@router.get("/{attendance_id}")
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    logger.info("event=attendance_get_request attendance_id=%s", attendance_id)
    record = attendance_service.get_attendance_by_id(db, attendance_id)
    return success(data=_serialize_record(record), message="Attendance record retrieved successfully")
