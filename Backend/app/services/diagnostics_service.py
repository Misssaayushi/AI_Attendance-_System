"""Phase 10 Step 1-2: Backend stability diagnostics and API coverage support."""

from __future__ import annotations

from datetime import datetime, timezone

from app.config import settings
from app.database.connection import test_db_connection
from app.scheduler import get_scheduler
from app.utils.logger import logger


def _scheduler_status() -> dict:
    try:
        scheduler = get_scheduler()
        return {
            "enabled": settings.SCHEDULER_ENABLED,
            "running": bool(scheduler.running) if settings.SCHEDULER_ENABLED else False,
            "timezone": settings.SCHEDULER_TIMEZONE,
        }
    except Exception:
        return {
            "enabled": settings.SCHEDULER_ENABLED,
            "running": False,
            "timezone": settings.SCHEDULER_TIMEZONE,
        }


def get_backend_readiness_snapshot() -> dict:
    """
    Lightweight system stability/readiness payload used for Phase 10 checks.
    """
    db_ok = test_db_connection()
    scheduler = _scheduler_status()
    readiness = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "debug_mode": settings.DEBUG_MODE,
            "api_prefix": settings.API_PREFIX,
            "cors_origins_count": len(settings.CORS_ALLOWED_ORIGINS),
        },
        "database": {
            "connected": db_ok,
        },
        "scheduler": scheduler,
        "automation": {
            "email_enabled": settings.EMAIL_ENABLED,
            "email_automation_enabled": settings.EMAIL_AUTOMATION_ENABLED,
            "analytics_perf_metrics": settings.ANALYTICS_ENABLE_PERF_METRICS,
        },
        "overall_status": "ready" if db_ok else "degraded",
    }
    logger.info(
        "event=backend_readiness_snapshot status=%s db_connected=%s scheduler_running=%s",
        readiness["overall_status"],
        readiness["database"]["connected"],
        readiness["scheduler"]["running"],
    )
    return readiness


def get_api_coverage_matrix() -> dict:
    """
    Structured API coverage map for Phase 10 test workflow.
    """
    coverage = {
        "authentication": [
            "POST /auth/login",
            "GET /auth/me",
            "POST /auth/logout",
        ],
        "students": [
            "GET /students/",
            "POST /students/",
            "GET /students/{student_id}",
            "PUT /students/{student_id}",
            "DELETE /students/{student_id}",
        ],
        "attendance": [
            "POST /attendance/mark",
            "GET /attendance/",
            "GET /attendance/summary/daily",
            "GET /attendance/student/{student_id}",
            "GET /attendance/{attendance_id}",
        ],
        "excel_and_exports": [
            "POST /attendance/export/template",
            "POST /attendance/export/monthly",
            "GET /attendance/export/preview",
        ],
        "scheduler_and_automation": [
            "GET /attendance/automation/executions",
            "GET /attendance/automation/summary",
        ],
        "email_reporting": [
            "POST /attendance/reports/email/monthly",
            "POST /attendance/reports/email/daily",
            "GET /attendance/reports/email/deliveries",
            "GET /attendance/reports/email/summary",
        ],
        "dashboard_analytics": [
            "GET /dashboard/summary",
            "GET /dashboard/stats/daily",
            "GET /dashboard/stats/monthly",
            "GET /dashboard/stats/department",
            "GET /dashboard/graphs/weekly",
            "GET /dashboard/graphs/monthly",
            "GET /dashboard/graphs/department",
            "GET /dashboard/monitoring/summary",
        ],
    }
    totals = {
        "groups": len(coverage),
        "endpoints": sum(len(v) for v in coverage.values()),
    }
    logger.info("event=api_coverage_matrix_generated groups=%s endpoints=%s", totals["groups"], totals["endpoints"])
    return {
        "coverage": coverage,
        "totals": totals,
    }

