"""Phase 9 Step 1-2: Dashboard analytics service (summary metrics)."""

from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from time import perf_counter

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.exceptions import AnalyticsQueryException, AnalyticsValidationException
from app.utils.analytics_filters import month_date_range, resolve_weekly_window, validate_year_month
from app.utils.logger import logger


def resolve_summary_date(target_date: date | None = None) -> date:
    return target_date or datetime.now(timezone.utc).date()


def _perf_meta(*, started_at: float) -> dict:
    if not settings.ANALYTICS_ENABLE_PERF_METRICS:
        return {}
    return {
        "duration_ms": int((perf_counter() - started_at) * 1000),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _base_student_query(db: Session, *, department: str | None = None):
    query = db.query(models.Student.id)
    if department:
        query = query.filter(models.Student.department == department)
    return query


def _present_count_for_date(db: Session, *, target_date: date, department: str | None = None) -> int:
    query = (
        db.query(func.count(distinct(models.Attendance.student_id)))
        .filter(
            models.Attendance.date == target_date,
            models.Attendance.status.in_(["Present", "Late"]),
        )
    )
    if department:
        query = query.join(models.Student, models.Student.id == models.Attendance.student_id).filter(
            models.Student.department == department
        )
    return query.scalar() or 0


def _attendance_stats_payload(*, total_students: int, present_count: int) -> dict:
    absent_count = max(total_students - present_count, 0)
    percentage = round((present_count / total_students) * 100, 2) if total_students > 0 else 0.0
    return {
        "total_students": total_students,
        "present": present_count,
        "absent": absent_count,
        "attendance_percentage": percentage,
    }


def get_dashboard_summary(
    db: Session,
    *,
    target_date: date | None = None,
    department: str | None = None,
) -> dict:
    """
    Returns dashboard KPI summary with efficient aggregate queries:
    - total_students
    - present_today
    - absent_today
    - attendance_percentage
    """
    started = perf_counter()
    try:
        summary_date = resolve_summary_date(target_date=target_date)

        total_students = _base_student_query(db, department=department).count()
        present_today = _present_count_for_date(db, target_date=summary_date, department=department)
        stats = _attendance_stats_payload(total_students=total_students, present_count=present_today)
    except Exception as exc:
        logger.exception("event=dashboard_summary_query_failed date=%s department=%s", target_date, department)
        raise AnalyticsQueryException(str(exc)) from exc

    logger.info(
        "event=dashboard_summary_generated date=%s department=%s total_students=%s present_today=%s absent_today=%s attendance_percentage=%s",
        summary_date.isoformat(),
        department,
        stats["total_students"],
        present_today,
        stats["absent"],
        stats["attendance_percentage"],
    )
    return {
        "date": summary_date.isoformat(),
        "department": department,
        "total_students": stats["total_students"],
        "present_today": present_today,
        "absent_today": stats["absent"],
        "attendance_percentage": stats["attendance_percentage"],
        "meta": _perf_meta(started_at=started),
    }


def get_daily_attendance_stats(
    db: Session,
    *,
    target_date: date | None = None,
    department: str | None = None,
) -> dict:
    started = perf_counter()
    try:
        stats_date = resolve_summary_date(target_date=target_date)
        total_students = _base_student_query(db, department=department).count()
        present_count = _present_count_for_date(db, target_date=stats_date, department=department)
        stats = _attendance_stats_payload(total_students=total_students, present_count=present_count)
    except Exception as exc:
        logger.exception("event=dashboard_daily_stats_query_failed date=%s department=%s", target_date, department)
        raise AnalyticsQueryException(str(exc)) from exc
    return {
        "date": stats_date.isoformat(),
        "department": department,
        "total_students": stats["total_students"],
        "present_students": stats["present"],
        "absent_students": stats["absent"],
        "attendance_percentage": stats["attendance_percentage"],
        "meta": _perf_meta(started_at=started),
    }


def get_monthly_attendance_stats(
    db: Session,
    *,
    year: int,
    month: int,
    department: str | None = None,
) -> dict:
    started = perf_counter()
    try:
        start_date, end_date = month_date_range(year=year, month=month)
    except ValueError as exc:
        raise AnalyticsValidationException(str(exc)) from exc
    try:
        total_students = _base_student_query(db, department=department).count()
        days_in_month = (end_date - start_date).days + 1

        present_query = (
            db.query(func.count(models.Attendance.id))
            .filter(
                models.Attendance.date >= start_date,
                models.Attendance.date <= end_date,
                models.Attendance.status.in_(["Present", "Late"]),
            )
        )
        if department:
            present_query = present_query.join(models.Student, models.Student.id == models.Attendance.student_id).filter(
                models.Student.department == department
            )
        present_records = present_query.scalar() or 0

        expected_records = total_students * days_in_month
        absent_records = max(expected_records - present_records, 0)
        percentage = round((present_records / expected_records) * 100, 2) if expected_records > 0 else 0.0
    except Exception as exc:
        logger.exception("event=dashboard_monthly_stats_query_failed year=%s month=%s department=%s", year, month, department)
        raise AnalyticsQueryException(str(exc)) from exc
    return {
        "year": year,
        "month": month,
        "department": department,
        "days_in_month": days_in_month,
        "total_students": total_students,
        "present_records": present_records,
        "absent_records": absent_records,
        "attendance_percentage": percentage,
        "meta": _perf_meta(started_at=started),
    }


def get_department_attendance_stats(
    db: Session,
    *,
    target_date: date | None = None,
) -> list[dict]:
    stats_date = resolve_summary_date(target_date=target_date)
    try:
        totals_rows = (
            db.query(models.Student.department, func.count(models.Student.id))
            .filter(models.Student.department.isnot(None))
            .group_by(models.Student.department)
            .all()
        )
        present_rows = (
            db.query(models.Student.department, func.count(distinct(models.Attendance.student_id)))
            .join(models.Attendance, models.Attendance.student_id == models.Student.id)
            .filter(
                models.Attendance.date == stats_date,
                models.Attendance.status.in_(["Present", "Late"]),
                models.Student.department.isnot(None),
            )
            .group_by(models.Student.department)
            .all()
        )
    except Exception as exc:
        logger.exception("event=dashboard_department_stats_query_failed date=%s", stats_date)
        raise AnalyticsQueryException(str(exc)) from exc

    totals_map = {row[0]: int(row[1]) for row in totals_rows}
    present_map = {row[0]: int(row[1]) for row in present_rows}
    rows: list[dict] = []
    for dept in sorted(totals_map.keys()):
        stats = _attendance_stats_payload(total_students=totals_map[dept], present_count=present_map.get(dept, 0))
        rows.append(
            {
                "department": dept,
                "total_students": stats["total_students"],
                "present_students": stats["present"],
                "absent_students": stats["absent"],
                "attendance_percentage": stats["attendance_percentage"],
            }
        )
    return rows


def get_weekly_trend_graph(
    db: Session,
    *,
    end_date: date | None = None,
    days: int = 7,
    department: str | None = None,
) -> dict:
    started = perf_counter()
    try:
        start_date, end_date_resolved = resolve_weekly_window(end_date=end_date, days=days)
    except ValueError as exc:
        raise AnalyticsValidationException(str(exc)) from exc
    try:
        total_students = _base_student_query(db, department=department).count()

        query = (
            db.query(models.Attendance.date, func.count(distinct(models.Attendance.student_id)))
            .filter(
                models.Attendance.date >= start_date,
                models.Attendance.date <= end_date_resolved,
                models.Attendance.status.in_(["Present", "Late"]),
            )
            .group_by(models.Attendance.date)
        )
        if department:
            query = query.join(models.Student, models.Student.id == models.Attendance.student_id).filter(
                models.Student.department == department
            )
        rows = query.all()
        present_by_date = {row[0]: int(row[1]) for row in rows}
    except Exception as exc:
        logger.exception("event=dashboard_weekly_graph_query_failed end_date=%s days=%s department=%s", end_date, days, department)
        raise AnalyticsQueryException(str(exc)) from exc

    labels: list[str] = []
    data: list[float] = []
    cursor = start_date
    while cursor <= end_date_resolved:
        labels.append(cursor.strftime("%a"))
        present_count = present_by_date.get(cursor, 0)
        pct = round((present_count / total_students) * 100, 2) if total_students > 0 else 0.0
        data.append(pct)
        cursor += timedelta(days=1)
    return {
        "range": {"from_date": start_date.isoformat(), "to_date": end_date_resolved.isoformat()},
        "department": department,
        "labels": labels,
        "data": data,
        "meta": _perf_meta(started_at=started),
    }


def get_monthly_trend_graph(
    db: Session,
    *,
    year: int,
    month: int,
    department: str | None = None,
) -> dict:
    started = perf_counter()
    try:
        validate_year_month(year=year, month=month)
        start_date, end_date = month_date_range(year=year, month=month)
    except ValueError as exc:
        raise AnalyticsValidationException(str(exc)) from exc
    try:
        total_students = _base_student_query(db, department=department).count()

        query = (
            db.query(models.Attendance.date, func.count(distinct(models.Attendance.student_id)))
            .filter(
                models.Attendance.date >= start_date,
                models.Attendance.date <= end_date,
                models.Attendance.status.in_(["Present", "Late"]),
            )
            .group_by(models.Attendance.date)
        )
        if department:
            query = query.join(models.Student, models.Student.id == models.Attendance.student_id).filter(
                models.Student.department == department
            )
        rows = query.all()
        present_by_date = {row[0]: int(row[1]) for row in rows}
    except Exception as exc:
        logger.exception("event=dashboard_monthly_graph_query_failed year=%s month=%s department=%s", year, month, department)
        raise AnalyticsQueryException(str(exc)) from exc

    labels: list[str] = []
    data: list[float] = []
    cursor = start_date
    while cursor <= end_date:
        labels.append(f"{cursor.day:02d}")
        present_count = present_by_date.get(cursor, 0)
        pct = round((present_count / total_students) * 100, 2) if total_students > 0 else 0.0
        data.append(pct)
        cursor += timedelta(days=1)
    return {
        "range": {"year": year, "month": month},
        "department": department,
        "labels": labels,
        "data": data,
        "meta": _perf_meta(started_at=started),
    }


def get_department_comparison_graph(
    db: Session,
    *,
    target_date: date | None = None,
) -> dict:
    started = perf_counter()
    stats_date = resolve_summary_date(target_date=target_date)
    rows = get_department_attendance_stats(db, target_date=stats_date)
    labels = [row["department"] for row in rows]
    data = [row["attendance_percentage"] for row in rows]
    return {
        "date": stats_date.isoformat(),
        "labels": labels,
        "data": data,
        "meta": _perf_meta(started_at=started),
    }


def get_analytics_monitoring_summary(db: Session) -> dict:
    """
    Lightweight monitoring payload for dashboard analytics health and scale.
    """
    try:
        total_students = db.query(func.count(models.Student.id)).scalar() or 0
        total_attendance_records = db.query(func.count(models.Attendance.id)).scalar() or 0
        latest_attendance_date = db.query(func.max(models.Attendance.date)).scalar()
    except Exception as exc:
        logger.exception("event=dashboard_monitoring_query_failed")
        raise AnalyticsQueryException(str(exc)) from exc
    return {
        "total_students": int(total_students),
        "total_attendance_records": int(total_attendance_records),
        "latest_attendance_date": latest_attendance_date.isoformat() if latest_attendance_date else None,
        "analytics_default_trend_days": settings.ANALYTICS_DEFAULT_TREND_DAYS,
        "analytics_max_trend_days": settings.ANALYTICS_MAX_TREND_DAYS,
    }
