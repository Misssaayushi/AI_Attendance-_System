"""Phase 8 Step 1-2: Email reporting service facade."""

from __future__ import annotations

from datetime import date
from time import perf_counter

from app import models
from app.config import settings
from app.exceptions import EmailAttachmentException, EmailConfigurationException, EmailDeliveryException
from app.email.attachment_service import AttachmentService
from app.email.report_orchestrator import EmailSendResult, ReportEmailOrchestrator
from app.email.types import ReportEmailRequest


def validate_email_configuration() -> None:
    try:
        settings.validate_email_settings()
    except ValueError as exc:
        raise EmailConfigurationException(str(exc)) from exc


def default_admin_recipients() -> list[str]:
    return settings.EMAIL_ADMIN_RECIPIENTS


def default_faculty_recipients() -> list[str]:
    return settings.EMAIL_FACULTY_RECIPIENTS


def send_attendance_report_email(request: ReportEmailRequest) -> EmailSendResult:
    validate_email_configuration()
    result = ReportEmailOrchestrator.send_report(request)
    if not result.success:
        raise EmailDeliveryException(result.error or result.error_type or "Unknown email delivery failure")
    return result


def _resolve_recipient_group(recipient_group: str) -> list[str]:
    if recipient_group == "admin":
        recipients = default_admin_recipients()
    elif recipient_group == "faculty":
        recipients = default_faculty_recipients()
    elif recipient_group == "all":
        recipients = list({*default_admin_recipients(), *default_faculty_recipients()})
    else:
        raise EmailConfigurationException("recipient_group must be one of: admin, faculty, all")
    if not recipients:
        raise EmailConfigurationException(f"No recipients configured for group: {recipient_group}")
    return recipients


def _get_delivery_record(db, *, report_type: str, report_date: date, recipient_group: str, report_label: str):
    return (
        db.query(models.EmailDelivery)
        .filter(
            models.EmailDelivery.report_type == report_type,
            models.EmailDelivery.report_date == report_date,
            models.EmailDelivery.recipient_group == recipient_group,
            models.EmailDelivery.report_label == report_label,
        )
        .first()
    )


def _begin_delivery(
    db,
    *,
    report_type: str,
    report_date: date,
    recipient_group: str,
    report_label: str,
):
    existing = _get_delivery_record(
        db,
        report_type=report_type,
        report_date=report_date,
        recipient_group=recipient_group,
        report_label=report_label,
    )
    if existing:
        return existing, False
    record = models.EmailDelivery(
        report_type=report_type,
        report_date=report_date,
        recipient_group=recipient_group,
        report_label=report_label,
        status="running",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, True


def _finalize_delivery(
    db,
    *,
    record,
    status: str,
    attempts: int = 1,
    recipients_count: int = 0,
    attachment_name: str | None = None,
    duration_ms: int = 0,
    error_message: str | None = None,
):
    from datetime import datetime, timezone

    record.status = status
    record.attempts = attempts
    record.recipients_count = recipients_count
    record.attachment_name = attachment_name
    record.duration_ms = duration_ms
    record.error_message = error_message
    record.finished_at = datetime.now(timezone.utc)
    db.commit()


def _send_with_audit(
    db,
    *,
    report_type: str,
    report_date: date,
    report_label: str,
    recipient_group: str,
    request: ReportEmailRequest,
    force_send: bool = False,
) -> dict:
    started = perf_counter()
    record, created = _begin_delivery(
        db,
        report_type=report_type,
        report_date=report_date,
        recipient_group=recipient_group,
        report_label=report_label,
    )
    if not created and record.status == "success" and not force_send:
        return {
            "report_type": report_type,
            "report_label": report_label,
            "report_date": report_date.isoformat(),
            "recipient_group": recipient_group,
            "email_sent": True,
            "skipped_duplicate": True,
            "attempts": record.attempts or 1,
            "recipients_count": record.recipients_count or 0,
            "attachment_name": record.attachment_name,
        }

    record.status = "running"
    record.error_message = None
    db.commit()

    try:
        result = send_attendance_report_email(request)
        duration_ms = int((perf_counter() - started) * 1000)
        _finalize_delivery(
            db,
            record=record,
            status="success",
            attempts=result.attempts,
            recipients_count=result.recipients_count,
            attachment_name=result.attachment_name,
            duration_ms=duration_ms,
        )
        return {
            "report_type": report_type,
            "report_label": report_label,
            "report_date": report_date.isoformat(),
            "recipient_group": recipient_group,
            "email_sent": True,
            "skipped_duplicate": False,
            "attempts": result.attempts,
            "recipients_count": result.recipients_count,
            "attachment_name": result.attachment_name,
            "duration_ms": duration_ms,
        }
    except Exception as exc:
        duration_ms = int((perf_counter() - started) * 1000)
        _finalize_delivery(
            db,
            record=record,
            status="failed",
            attempts=settings.EMAIL_RETRY_LIMIT + 1,
            recipients_count=len(request.recipients),
            attachment_name=None,
            duration_ms=duration_ms,
            error_message=str(exc)[:500],
        )
        raise


def send_monthly_report_email(
    db,
    *,
    year: int,
    month: int,
    recipient_group: str = "admin",
    department: str | None = None,
    student_id: int | None = None,
    force_send: bool = False,
) -> dict:
    from app.services import excel_service

    recipients = _resolve_recipient_group(recipient_group)
    if department:
        report = excel_service.generate_department_monthly_report(db, year=year, month=month, department=department)
        report_type = "department"
        label = department
    elif student_id:
        report = excel_service.generate_student_monthly_report(db, year=year, month=month, student_id=student_id)
        report_type = "department"
        label = f"student_{student_id}"
    else:
        report = excel_service.generate_monthly_workbook_from_db(db, year=year, month=month)
        report_type = "monthly"
        label = "all_students"

    attachment_path = report["file_path"]
    try:
        AttachmentService.validate_report_attachment(attachment_path)
    except (FileNotFoundError, ValueError) as exc:
        raise EmailAttachmentException(str(exc)) from exc

    return _send_with_audit(
        db,
        report_type=report_type,
        report_date=date(year, month, 1),
        report_label=label,
        recipient_group=recipient_group,
        request=ReportEmailRequest(
            report_type=report_type,  # type: ignore[arg-type]
            report_label=label,
            attachment_path=attachment_path,
            recipients=recipients,
            date_label=f"{year:04d}-{month:02d}",
            summary=report.get("performance"),
        ),
        force_send=force_send,
    ) | {"file_path": attachment_path, "recipients": recipients}


def send_daily_report_email(
    db,
    *,
    target_date: date,
    recipient_group: str = "admin",
    force_send: bool = False,
) -> dict:
    from app.services import excel_service

    recipients = _resolve_recipient_group(recipient_group)
    report = excel_service.generate_monthly_workbook_from_db(
        db,
        year=target_date.year,
        month=target_date.month,
    )
    attachment_path = report["file_path"]
    try:
        AttachmentService.validate_report_attachment(attachment_path)
    except (FileNotFoundError, ValueError) as exc:
        raise EmailAttachmentException(str(exc)) from exc

    return _send_with_audit(
        db,
        report_type="daily",
        report_date=target_date,
        report_label="all_students",
        recipient_group=recipient_group,
        request=ReportEmailRequest(
            report_type="daily",
            report_label="all_students",
            attachment_path=attachment_path,
            recipients=recipients,
            date_label=target_date.isoformat(),
            summary={"records_scanned": report["performance"]["records_scanned"]},
        ),
        force_send=force_send,
    ) | {"file_path": attachment_path, "recipients": recipients}


def list_email_deliveries(db, *, limit: int = 50) -> list[models.EmailDelivery]:
    return db.query(models.EmailDelivery).order_by(models.EmailDelivery.report_date.desc()).limit(limit).all()


def get_email_delivery_summary(db, *, last_n: int = 50) -> dict:
    rows = list_email_deliveries(db, limit=last_n)
    return compute_email_delivery_summary_from_rows(rows)


def compute_email_delivery_summary_from_rows(rows: list[models.EmailDelivery]) -> dict:
    if not rows:
        return {
            "runs": 0,
            "success_runs": 0,
            "failed_runs": 0,
            "skipped_runs": 0,
            "avg_duration_ms": 0,
            "success_rate_pct": 0,
        }
    success = sum(1 for r in rows if r.status == "success")
    failed = sum(1 for r in rows if r.status == "failed")
    skipped = sum(1 for r in rows if r.status == "skipped")
    durations = [r.duration_ms for r in rows if r.duration_ms is not None]
    return {
        "runs": len(rows),
        "success_runs": success,
        "failed_runs": failed,
        "skipped_runs": skipped,
        "avg_duration_ms": int(sum(durations) / len(durations)) if durations else 0,
        "success_rate_pct": round((success / len(rows)) * 100, 2),
    }
