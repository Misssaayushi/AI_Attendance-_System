"""Phase 7 Step 1: Scheduler job registration utilities."""

from __future__ import annotations

import time

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database.connection import SessionLocal
from app.services.auto_absent_service import run_daily_auto_absent
from app.utils.logger import logger


AUTO_ABSENT_JOB_ID = "auto_absent_daily_job"


def auto_absent_job_stub() -> None:
    """
    Phase 7 Step 3-4 job entrypoint:
    Runs daily auto-absent workflow using a dedicated DB session.
    """
    logger.info("event=auto_absent_job_started")
    retries = settings.AUTO_ABSENT_RETRY_LIMIT
    max_attempts = retries + 1
    for attempt in range(1, max_attempts + 1):
        db = SessionLocal()
        try:
            result = run_daily_auto_absent(db, attempt_count=attempt)
            logger.info(
                "event=auto_absent_job_finished run_date=%s status=%s auto_absent_marked=%s excel_synced=%s attempt=%s/%s duration_ms=%s",
                result.run_date,
                result.status,
                result.auto_absent_marked,
                result.excel_synced,
                attempt,
                max_attempts,
                result.duration_ms,
            )
            return
        except Exception as exc:
            logger.exception(
                "event=auto_absent_job_attempt_failed attempt=%s/%s message=%s",
                attempt,
                max_attempts,
                str(exc),
            )
            if attempt == max_attempts:
                logger.error("event=auto_absent_job_exhausted_retries max_attempts=%s", max_attempts)
                return
            time.sleep(min(2**attempt, 10))
        finally:
            db.close()


def register_scheduler_jobs(scheduler: BaseScheduler) -> None:
    """Register scheduler jobs once, preventing duplicate registrations."""
    existing = scheduler.get_job(AUTO_ABSENT_JOB_ID)
    if existing is not None:
        logger.info("event=scheduler_job_exists job_id=%s", AUTO_ABSENT_JOB_ID)
        return

    trigger = CronTrigger(
        hour=settings.AUTO_ABSENT_HOUR,
        minute=settings.AUTO_ABSENT_MINUTE,
        timezone=settings.SCHEDULER_TIMEZONE,
    )
    scheduler.add_job(
        auto_absent_job_stub,
        trigger=trigger,
        id=AUTO_ABSENT_JOB_ID,
        replace_existing=False,
        coalesce=settings.SCHEDULER_COALESCE,
        max_instances=settings.SCHEDULER_MAX_INSTANCES,
        misfire_grace_time=3600,
    )
    logger.info(
        "event=scheduler_job_registered job_id=%s hour=%s minute=%s timezone=%s",
        AUTO_ABSENT_JOB_ID,
        settings.AUTO_ABSENT_HOUR,
        settings.AUTO_ABSENT_MINUTE,
        settings.SCHEDULER_TIMEZONE,
    )
