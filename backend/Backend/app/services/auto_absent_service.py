"""Phase 7 Step 3-4: Daily auto-absent workflow and service logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from time import perf_counter
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.exceptions import ExcelWriteException
from app.services import excel_service
from app.utils.logger import logger

AUTO_ABSENT_JOB_NAME = "auto_absent_daily"


@dataclass
class AutoAbsentResult:
    run_date: str
    total_students: int
    already_marked: int
    auto_absent_marked: int
    duplicate_skipped: int
    excel_synced: int
    status: str
    execution_skipped: bool = False
    duration_ms: int = 0
    attempt_count: int = 1


def _now_in_scheduler_timezone() -> datetime:
    return datetime.now(ZoneInfo(settings.SCHEDULER_TIMEZONE))


def resolve_target_date(target_date: date | None = None) -> date:
    return target_date or _now_in_scheduler_timezone().date()


def _resolve_absent_time(class_end_time: time | None = None) -> time:
    if class_end_time:
        return class_end_time
    return time(hour=settings.AUTO_ABSENT_HOUR, minute=settings.AUTO_ABSENT_MINUTE, second=0)


def identify_unmarked_student_ids(all_student_ids: list[int], marked_student_ids: set[int]) -> list[int]:
    return [student_id for student_id in all_student_ids if student_id not in marked_student_ids]


def _fetch_student_ids(db: Session) -> list[int]:
    rows = db.query(models.Student.id).order_by(models.Student.id.asc()).all()
    return [row[0] for row in rows]


def _fetch_marked_student_ids(db: Session, *, target_date: date) -> set[int]:
    rows = db.query(models.Attendance.student_id).filter(models.Attendance.date == target_date).all()
    return {row[0] for row in rows}


def _insert_absent_records(db: Session, *, target_date: date, student_ids: list[int], absent_time: time) -> tuple[int, int, list[int]]:
    """
    Inserts Absent records in batches. On unique-key conflicts, falls back to per-row inserts
    to preserve progress and count duplicate skips accurately.
    """
    if not student_ids:
        return 0, 0

    marked_count = 0
    duplicate_skipped = 0
    inserted_student_ids: list[int] = []
    batch_size = settings.AUTO_ABSENT_BATCH_SIZE

    for idx in range(0, len(student_ids), batch_size):
        batch = student_ids[idx : idx + batch_size]
        records = [
            models.Attendance(
                student_id=student_id,
                date=target_date,
                time=absent_time,
                status="Absent",
            )
            for student_id in batch
        ]
        try:
            db.add_all(records)
            db.commit()
            marked_count += len(records)
            inserted_student_ids.extend(batch)
            continue
        except IntegrityError:
            db.rollback()

        # Fallback insert per row to isolate duplicates while still progressing.
        for student_id in batch:
            try:
                db.add(
                    models.Attendance(
                        student_id=student_id,
                        date=target_date,
                        time=absent_time,
                        status="Absent",
                    )
                )
                db.commit()
                marked_count += 1
                inserted_student_ids.append(student_id)
            except IntegrityError:
                db.rollback()
                duplicate_skipped += 1

    return marked_count, duplicate_skipped, inserted_student_ids


def _get_execution_for_date(db: Session, *, run_date: date):
    return (
        db.query(models.SchedulerExecution)
        .filter(
            models.SchedulerExecution.job_name == AUTO_ABSENT_JOB_NAME,
            models.SchedulerExecution.run_date == run_date,
        )
        .first()
    )


def _begin_execution_lock(db: Session, *, run_date: date):
    execution = _get_execution_for_date(db, run_date=run_date)
    if execution:
        return execution, False
    execution = models.SchedulerExecution(
        job_name=AUTO_ABSENT_JOB_NAME,
        run_date=run_date,
        status="running",
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution, True


def _finalize_execution(
    db: Session,
    *,
    execution,
    status: str,
    total_students: int,
    already_marked: int,
    auto_absent_marked: int,
    duplicate_skipped: int,
    excel_synced: int,
    attempt_count: int = 1,
    duration_ms: int = 0,
    error_message: str | None = None,
):
    execution.status = status
    execution.total_students = total_students
    execution.already_marked = already_marked
    execution.auto_absent_marked = auto_absent_marked
    execution.duplicate_skipped = duplicate_skipped
    execution.excel_synced = excel_synced
    execution.attempt_count = attempt_count
    execution.duration_ms = duration_ms
    execution.error_message = error_message
    execution.finished_at = datetime.now(timezone.utc)
    db.commit()


def run_auto_absent_for_date(
    db: Session,
    *,
    target_date: date | None = None,
    attempt_count: int = 1,
) -> AutoAbsentResult:
    """
    Core workflow:
    Fetch rules -> filter students whose class ended -> find unmarked -> insert absentees -> sync Excel.
    """
    from app.services import class_timing_service
    
    run_date = resolve_target_date(target_date=target_date)
    started = perf_counter()

    if run_date.weekday() == 6:  # 6 is Sunday
        logger.info("event=auto_absent_execution_skipped reason=sunday run_date=%s", run_date.isoformat())
        return AutoAbsentResult(
            run_date=run_date.isoformat(),
            total_students=0,
            already_marked=0,
            auto_absent_marked=0,
            duplicate_skipped=0,
            excel_synced=0,
            status="success",
            execution_skipped=True,
            duration_ms=0,
            attempt_count=attempt_count,
        )

    execution, created = _begin_execution_lock(db, run_date=run_date)

    # Prevent repeated daily execution once already successful.
    if not created and execution.status == "success":
        logger.info("event=auto_absent_execution_skipped reason=already_success run_date=%s", run_date.isoformat())
        return AutoAbsentResult(
            run_date=run_date.isoformat(),
            total_students=execution.total_students or 0,
            already_marked=execution.already_marked or 0,
            auto_absent_marked=execution.auto_absent_marked or 0,
            duplicate_skipped=execution.duplicate_skipped or 0,
            excel_synced=execution.excel_synced or 0,
            status="success",
            execution_skipped=True,
            duration_ms=execution.duration_ms or 0,
            attempt_count=execution.attempt_count or 1,
        )

    # Reset stale existing lock state for rerun.
    execution.status = "running"
    execution.error_message = None
    execution.started_at = datetime.now(timezone.utc)
    execution.finished_at = None
    db.commit()

    try:
        # 1. Fetch rules and current time
        all_rules = class_timing_service.get_all_timings(db)
        global_rule = next((r for r in all_rules if r.department is None and r.semester is None), None)
        specific_rules = [r for r in all_rules if r.is_active and (r.department is not None or r.semester is not None)]
        
        current_time = _now_in_scheduler_timezone().time()
        
        # 2. Get students whose class has ended
        students = db.query(models.Student).all()
        eligible_students = []
        student_absent_time_map = {}
        
        for student in students:
            # Find applicable rule
            rule = next(
                (r for r in specific_rules if r.department == student.department and r.semester == student.semester), 
                global_rule
            )
            
            end_time = rule.class_end_time if rule else time(16, 0, 0) # Fallback 4 PM
            
            if current_time > end_time:
                eligible_students.append(student.id)
                student_absent_time_map[student.id] = end_time

        marked_ids = _fetch_marked_student_ids(db, target_date=run_date)
        unmarked_ids = identify_unmarked_student_ids(eligible_students, marked_ids)

        # Group unmarked IDs by their absent_time to insert in batches
        from collections import defaultdict
        time_to_students = defaultdict(list)
        for sid in unmarked_ids:
            time_to_students[student_absent_time_map[sid]].append(sid)

        auto_absent_marked = 0
        duplicate_skipped = 0
        inserted_student_ids = []
        
        for absent_time, sids in time_to_students.items():
            marked, skipped, inserted = _insert_absent_records(
                db,
                target_date=run_date,
                student_ids=sids,
                absent_time=absent_time
            )
            auto_absent_marked += marked
            duplicate_skipped += skipped
            inserted_student_ids.extend(inserted)

        excel_synced = 0
        final_status = "success"
        try:
            excel_synced = excel_service.sync_absent_students_for_date(
                db,
                target_date=run_date,
                student_ids=inserted_student_ids,
            )
        except ExcelWriteException:
            logger.exception("event=auto_absent_excel_sync_failed run_date=%s", run_date.isoformat())
            final_status = "partial"

        duration_ms = int((perf_counter() - started) * 1000)
        _finalize_execution(
            db,
            execution=execution,
            status=final_status,
            total_students=len(eligible_students),
            already_marked=len(marked_ids.intersection(set(eligible_students))),
            auto_absent_marked=auto_absent_marked,
            duplicate_skipped=duplicate_skipped,
            excel_synced=excel_synced,
            attempt_count=attempt_count,
            duration_ms=duration_ms,
            error_message=None if final_status == "success" else "excel_sync_failed",
        )

        result = AutoAbsentResult(
            run_date=run_date.isoformat(),
            total_students=len(eligible_students),
            already_marked=len(marked_ids.intersection(set(eligible_students))),
            auto_absent_marked=auto_absent_marked,
            duplicate_skipped=duplicate_skipped,
            excel_synced=excel_synced,
            status=final_status,
            duration_ms=duration_ms,
            attempt_count=attempt_count,
        )
    except Exception as exc:
        duration_ms = int((perf_counter() - started) * 1000)
        _finalize_execution(
            db,
            execution=execution,
            status="failed",
            total_students=0,
            already_marked=0,
            auto_absent_marked=0,
            duplicate_skipped=0,
            excel_synced=0,
            attempt_count=attempt_count,
            duration_ms=duration_ms,
            error_message=str(exc)[:500],
        )
        logger.exception("event=auto_absent_run_failed run_date=%s", run_date.isoformat())
        raise
    logger.info(
        "event=auto_absent_run_completed run_date=%s total_students=%s already_marked=%s auto_absent_marked=%s duplicate_skipped=%s excel_synced=%s",
        result.run_date,
        result.total_students,
        result.already_marked,
        result.auto_absent_marked,
        result.duplicate_skipped,
        result.excel_synced,
    )
    return result


def run_daily_auto_absent(db: Session, *, attempt_count: int = 1) -> AutoAbsentResult:
    return run_auto_absent_for_date(db, target_date=None, attempt_count=attempt_count)


def list_scheduler_executions(db: Session, *, limit: int = 30) -> list[models.SchedulerExecution]:
    return (
        db.query(models.SchedulerExecution)
        .filter(models.SchedulerExecution.job_name == AUTO_ABSENT_JOB_NAME)
        .order_by(models.SchedulerExecution.run_date.desc())
        .limit(limit)
        .all()
    )


def get_scheduler_summary(db: Session, *, last_n: int = 30) -> dict:
    executions = list_scheduler_executions(db, limit=last_n)
    return compute_scheduler_summary_from_rows(executions)


def compute_scheduler_summary_from_rows(executions: list[models.SchedulerExecution]) -> dict:
    if not executions:
        return {
            "runs": 0,
            "success_runs": 0,
            "partial_runs": 0,
            "failed_runs": 0,
            "avg_duration_ms": 0,
            "avg_auto_absent_marked": 0,
            "success_rate_pct": 0,
        }

    success_runs = sum(1 for e in executions if e.status == "success")
    partial_runs = sum(1 for e in executions if e.status == "partial")
    failed_runs = sum(1 for e in executions if e.status == "failed")
    durations = [e.duration_ms for e in executions if e.duration_ms is not None]
    absent_counts = [e.auto_absent_marked for e in executions if e.auto_absent_marked is not None]
    return {
        "runs": len(executions),
        "success_runs": success_runs,
        "partial_runs": partial_runs,
        "failed_runs": failed_runs,
        "avg_duration_ms": int(sum(durations) / len(durations)) if durations else 0,
        "avg_auto_absent_marked": int(sum(absent_counts) / len(absent_counts)) if absent_counts else 0,
        "success_rate_pct": round((success_runs / len(executions)) * 100, 2),
    }
