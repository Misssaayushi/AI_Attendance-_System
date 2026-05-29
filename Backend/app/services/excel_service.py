"""Phase 6 Step 1-2 service wrapper for workbook template generation."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from time import perf_counter

import pandas as pd
from sqlalchemy.orm import Session, joinedload

from app import models
from app.config import settings
from app.exceptions import (
    AttendanceNotFoundException,
    ExcelExportException,
    ExcelTemplateValidationException,
    ExcelWriteException,
)
from app.exports.excel_automation import (
    ExcelAutomationConfig,
    AttendanceWriter,
    DateColumnManager,
    METADATA_SHEET_NAME,
    PRIMARY_SHEET_NAME,
    SUMMARY_SHEET_NAME,
    WorkbookManager,
)
from app.utils.logger import logger

DEFAULT_EXPORT_BATCH_SIZE = 1000


def _validate_year_month(year: int, month: int) -> None:
    if year < 2000 or year > 2100:
        raise ExcelTemplateValidationException("year must be between 2000 and 2100")
    if month < 1 or month > 12:
        raise ExcelTemplateValidationException("month must be between 1 and 12")


def generate_monthly_workbook_template(*, year: int, month: int) -> str:
    """
    Generates a monthly attendance workbook template and saves it to EXPORT_DIR.
    Returns the absolute file path of the generated workbook.
    """
    _validate_year_month(year, month)
    config = ExcelAutomationConfig(export_dir=settings.EXPORT_DIR)
    try:
        workbook = WorkbookManager.create_monthly_workbook(year=year, month=month, config=config)
        output_path = WorkbookManager.save_monthly_workbook(
            workbook,
            year=year,
            month=month,
            config=config,
        )
    except Exception as exc:
        logger.exception("event=monthly_workbook_template_failed year=%s month=%s", year, month)
        raise ExcelWriteException("Failed to generate monthly workbook template") from exc
    logger.info("event=monthly_workbook_template_generated year=%s month=%s path=%s", year, month, output_path)
    return output_path


def _month_date_range(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    return start, end


def _iter_in_batches(items: list, batch_size: int = DEFAULT_EXPORT_BATCH_SIZE):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def sync_attendance_record_to_monthly_workbook(
    db: Session,
    *,
    attendance_id: int,
    year: int,
    month: int,
) -> dict:
    """
    Step 5:
    Upserts a single attendance record into the target monthly workbook.
    """
    _validate_year_month(year, month)
    record = (
        db.query(models.Attendance)
        .options(joinedload(models.Attendance.student))
        .filter(models.Attendance.id == attendance_id)
        .first()
    )
    if not record:
        raise AttendanceNotFoundException("Attendance record not found for Excel sync")
    if record.student is None:
        raise ExcelExportException("Attendance record has no linked student")

    config = ExcelAutomationConfig(export_dir=settings.EXPORT_DIR)
    wb = WorkbookManager.load_or_create_monthly_workbook(year=year, month=month, config=config)
    sheet = wb[PRIMARY_SHEET_NAME]
    day_map = DateColumnManager.ensure_day_columns(sheet, year=year, month=month)

    try:
        row_map: dict[str, int] = {}
        result = AttendanceWriter.upsert_attendance_cell(
            sheet=sheet,
            year=year,
            month=month,
            student={
                "student_id": record.student.id,
                "roll_number": record.student.roll_number,
                "student_name": record.student.full_name,
                "department": record.student.department,
                "course": record.student.course,
                "year_batch": record.student.year_batch,
                "semester": record.student.semester,
                "section": record.student.section,
            },
            attendance_date=record.date,
            status=record.status,
            row_map=row_map,
            day_column_map=day_map,
        )
        output_path = WorkbookManager.save_monthly_workbook(wb, year=year, month=month, config=config)
    except Exception as exc:
        logger.exception("event=attendance_record_excel_sync_failed attendance_id=%s", attendance_id)
        raise ExcelWriteException("Failed to sync attendance record to workbook") from exc
    logger.info(
        "event=attendance_record_synced_to_excel attendance_id=%s year=%s month=%s action=%s path=%s",
        attendance_id,
        year,
        month,
        result["action"],
        output_path,
    )
    return {"file_path": output_path, "result": result}


def generate_monthly_workbook_from_db(
    db: Session,
    *,
    year: int,
    month: int,
    department: str | None = None,
    student_id: int | None = None,
) -> dict:
    """
    Step 6:
    Generates complete monthly workbook from student roster + month attendance.
    """
    _validate_year_month(year, month)
    month_start, month_end = _month_date_range(year, month)
    started_at = perf_counter()

    student_query = db.query(models.Student)
    if department:
        student_query = student_query.filter(models.Student.department == department)
    if student_id:
        student_query = student_query.filter(models.Student.id == student_id)
    students = student_query.order_by(models.Student.roll_number.asc()).all()

    student_ids = [s.id for s in students]
    attendance_query = (
        db.query(models.Attendance)
        .options(joinedload(models.Attendance.student))
        .filter(models.Attendance.date >= month_start, models.Attendance.date <= month_end)
    )
    if student_ids:
        attendance_query = attendance_query.filter(models.Attendance.student_id.in_(student_ids))
    else:
        attendance_query = attendance_query.filter(models.Attendance.student_id == -1)
    records = attendance_query.order_by(models.Attendance.date.asc(), models.Attendance.time.asc()).all()

    config = ExcelAutomationConfig(export_dir=settings.EXPORT_DIR)
    try:
        wb = WorkbookManager.create_monthly_workbook(year=year, month=month, config=config)
        sheet = wb[PRIMARY_SHEET_NAME]
        day_map = DateColumnManager.ensure_day_columns(sheet, year=year, month=month)
        row_map: dict[str, int] = {}

        for batch in _iter_in_batches(students):
            for student in batch:
                AttendanceWriter.ensure_student_row_with_cache(
                    sheet=sheet,
                    student={
                        "student_id": student.id,
                        "roll_number": student.roll_number,
                        "student_name": student.full_name,
                        "department": student.department,
                        "course": student.course,
                        "year_batch": student.year_batch,
                        "semester": student.semester,
                        "section": student.section,
                    },
                    row_map=row_map,
                )

        updated_count = 0
        for batch in _iter_in_batches(records):
            for record in batch:
                if record.student is None:
                    continue
                result = AttendanceWriter.upsert_attendance_cell(
                    sheet=sheet,
                    year=year,
                    month=month,
                    student={
                        "student_id": record.student.id,
                        "roll_number": record.student.roll_number,
                        "student_name": record.student.full_name,
                        "department": record.student.department,
                        "course": record.student.course,
                        "year_batch": record.student.year_batch,
                        "semester": record.student.semester,
                        "section": record.student.section,
                    },
                    attendance_date=record.date,
                    status=record.status,
                    row_map=row_map,
                    day_column_map=day_map,
                )
                if result["action"] in {"created", "updated"}:
                    updated_count += 1

        if SUMMARY_SHEET_NAME in wb.sheetnames:
            summary = wb[SUMMARY_SHEET_NAME]
            summary.cell(row=2, column=1, value="Total Students")
            summary.cell(row=2, column=2, value=len(students))
            summary.cell(row=3, column=1, value="Attendance Records Applied")
            summary.cell(row=3, column=2, value=updated_count)
            if records:
                df = pd.DataFrame({"status": [r.status for r in records]})
                counts = df["status"].value_counts().to_dict()
                summary.cell(row=4, column=1, value="Present Count")
                summary.cell(row=4, column=2, value=counts.get("Present", 0))
                summary.cell(row=5, column=1, value="Absent Count")
                summary.cell(row=5, column=2, value=counts.get("Absent", 0))
                summary.cell(row=6, column=1, value="Late Count")
                summary.cell(row=6, column=2, value=counts.get("Late", 0))

        if METADATA_SHEET_NAME in wb.sheetnames:
            metadata = wb[METADATA_SHEET_NAME]
            metadata.cell(row=4, column=1, value="student_filter_department")
            metadata.cell(row=4, column=2, value=department)
            metadata.cell(row=5, column=1, value="student_filter_id")
            metadata.cell(row=5, column=2, value=student_id)

        output_path = WorkbookManager.save_monthly_workbook(wb, year=year, month=month, config=config)
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
    except ExcelTemplateValidationException:
        raise
    except Exception as exc:
        logger.exception("event=monthly_workbook_generation_failed year=%s month=%s", year, month)
        raise ExcelWriteException("Failed to generate monthly workbook from database") from exc
    logger.info(
        "event=monthly_workbook_generated year=%s month=%s students=%s records=%s path=%s",
        year,
        month,
        len(students),
        updated_count,
        output_path,
    )
    return {
        "file_path": output_path,
        "year": year,
        "month": month,
        "students": len(students),
        "records_applied": updated_count,
        "performance": {
            "duration_ms": duration_ms,
            "batch_size": DEFAULT_EXPORT_BATCH_SIZE,
            "student_rows_seeded": len(students),
            "records_scanned": len(records),
        },
    }


def generate_department_monthly_report(
    db: Session,
    *,
    year: int,
    month: int,
    department: str,
) -> dict:
    if not department or not department.strip():
        raise ExcelTemplateValidationException("department is required")
    return generate_monthly_workbook_from_db(
        db,
        year=year,
        month=month,
        department=department.strip(),
    )


def generate_student_monthly_report(
    db: Session,
    *,
    year: int,
    month: int,
    student_id: int,
) -> dict:
    if student_id <= 0:
        raise ExcelTemplateValidationException("student_id must be greater than 0")
    return generate_monthly_workbook_from_db(
        db,
        year=year,
        month=month,
        student_id=student_id,
    )


def sync_absent_students_for_date(
    db: Session,
    *,
    target_date: date,
    student_ids: list[int],
) -> int:
    """
    Step 7 prep hook:
    Syncs absent status for given students on target_date into monthly workbook.
    Returns count of attempted row updates.
    """
    if not student_ids:
        return 0

    year = target_date.year
    month = target_date.month
    _validate_year_month(year, month)

    students = db.query(models.Student).filter(models.Student.id.in_(student_ids)).all()
    if not students:
        return 0

    config = ExcelAutomationConfig(export_dir=settings.EXPORT_DIR)
    try:
        wb = WorkbookManager.load_or_create_monthly_workbook(year=year, month=month, config=config)
        sheet = wb[PRIMARY_SHEET_NAME]
        day_map = DateColumnManager.ensure_day_columns(sheet, year=year, month=month)
        row_map: dict[str, int] = {}

        for student in students:
            AttendanceWriter.upsert_attendance_cell(
                sheet=sheet,
                year=year,
                month=month,
                student={
                    "student_id": student.id,
                    "roll_number": student.roll_number,
                    "student_name": student.full_name,
                    "department": student.department,
                    "course": student.course,
                    "year_batch": student.year_batch,
                    "semester": student.semester,
                    "section": student.section,
                },
                attendance_date=target_date,
                status="Absent",
                row_map=row_map,
                day_column_map=day_map,
            )
        WorkbookManager.save_monthly_workbook(wb, year=year, month=month, config=config)
        return len(students)
    except Exception as exc:
        logger.exception(
            "event=excel_absent_sync_failed date=%s student_count=%s",
            target_date.isoformat(),
            len(student_ids),
        )
        raise ExcelWriteException("Failed to sync absent students to workbook") from exc
