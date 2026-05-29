from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.middleware.auth_deps import get_current_admin
from app.services import dashboard_analytics_service
from app.utils.logger import logger
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/summary")
def dashboard_summary(
    target_date: date | None = Query(default=None),
    department: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_summary_request date=%s department=%s", target_date, department)
    data = dashboard_analytics_service.get_dashboard_summary(
        db,
        target_date=target_date,
        department=department,
    )
    return success(data=data, message="Analytics Retrieved Successfully")


@router.get("/stats/daily")
def daily_attendance_stats(
    target_date: date | None = Query(default=None),
    department: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_daily_stats_request date=%s department=%s", target_date, department)
    data = dashboard_analytics_service.get_daily_attendance_stats(
        db,
        target_date=target_date,
        department=department,
    )
    return success(data=data, message="Daily Analytics Retrieved Successfully")


@router.get("/stats/monthly")
def monthly_attendance_stats(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    department: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_monthly_stats_request year=%s month=%s department=%s", year, month, department)
    data = dashboard_analytics_service.get_monthly_attendance_stats(
        db,
        year=year,
        month=month,
        department=department,
    )
    return success(data=data, message="Monthly Analytics Retrieved Successfully")


@router.get("/stats/department")
def department_attendance_stats(
    target_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_department_stats_request date=%s", target_date)
    items = dashboard_analytics_service.get_department_attendance_stats(
        db,
        target_date=target_date,
    )
    return success(
        data={"date": (target_date.isoformat() if target_date else None), "items": items, "count": len(items)},
        message="Department Analytics Retrieved Successfully",
    )


@router.get("/graphs/weekly")
def weekly_trend_graph(
    end_date: date | None = Query(default=None),
    days: int = Query(settings.ANALYTICS_DEFAULT_TREND_DAYS, ge=2, le=settings.ANALYTICS_MAX_TREND_DAYS),
    department: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_weekly_graph_request end_date=%s days=%s department=%s", end_date, days, department)
    data = dashboard_analytics_service.get_weekly_trend_graph(
        db,
        end_date=end_date,
        days=days,
        department=department,
    )
    return success(data=data, message="Weekly Trend Retrieved Successfully")


@router.get("/graphs/monthly")
def monthly_trend_graph(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    department: str | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_monthly_graph_request year=%s month=%s department=%s", year, month, department)
    data = dashboard_analytics_service.get_monthly_trend_graph(
        db,
        year=year,
        month=month,
        department=department,
    )
    return success(data=data, message="Monthly Trend Retrieved Successfully")


@router.get("/graphs/department")
def department_comparison_graph(
    target_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_department_graph_request date=%s", target_date)
    data = dashboard_analytics_service.get_department_comparison_graph(
        db,
        target_date=target_date,
    )
    return success(data=data, message="Department Comparison Retrieved Successfully")


@router.get("/monitoring/summary")
def analytics_monitoring_summary(
    db: Session = Depends(get_db),
):
    logger.info("event=dashboard_monitoring_summary_request")
    data = dashboard_analytics_service.get_analytics_monitoring_summary(db)
    return success(data=data, message="Analytics Monitoring Retrieved Successfully")
