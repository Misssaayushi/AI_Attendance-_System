"""Phase 7 Step 1: Scheduler job registration utilities."""

from __future__ import annotations

import time
from datetime import date

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database.connection import SessionLocal
from app.services.auto_absent_service import run_daily_auto_absent
from app.services import email_service
from app.utils.logger import logger


AUTO_ABSENT_JOB_ID = "auto_absent_daily_job"
MONTHLY_EMAIL_JOB_ID = "monthly_report_email_job"


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
            if settings.EMAIL_AUTOMATION_ENABLED and settings.EMAIL_ENABLED and not result.execution_skipped:
                try:
                    target_date = date.fromisoformat(result.run_date)
                    email_result = email_service.send_daily_report_email(
                        db,
                        target_date=target_date,
                        recipient_group=settings.EMAIL_DAILY_RECIPIENT_GROUP,
                    )
                    logger.info(
                        "event=auto_absent_daily_email_sent run_date=%s attempts=%s recipients=%s",
                        result.run_date,
                        email_result.get("attempts"),
                        len(email_result.get("recipients", [])),
                    )
                except Exception as exc:
                    logger.exception("event=auto_absent_daily_email_failed run_date=%s message=%s", result.run_date, str(exc))
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


def monthly_report_email_job() -> None:
    if not settings.EMAIL_AUTOMATION_ENABLED or not settings.EMAIL_MONTHLY_AUTOMATION_ENABLED or not settings.EMAIL_ENABLED:
        return
    db = SessionLocal()
    try:
        now = date.today()
        year = now.year
        month = now.month
        email_result = email_service.send_monthly_report_email(
            db,
            year=year,
            month=month,
            recipient_group=settings.EMAIL_MONTHLY_RECIPIENT_GROUP,
        )
        logger.info(
            "event=monthly_email_job_finished year=%s month=%s attempts=%s recipients=%s",
            year,
            month,
            email_result.get("attempts"),
            len(email_result.get("recipients", [])),
        )
    except Exception as exc:
        logger.exception("event=monthly_email_job_failed message=%s", str(exc))
    finally:
        db.close()


def register_scheduler_jobs(scheduler: BaseScheduler) -> None:
    """Register scheduler jobs once, preventing duplicate registrations."""
    existing = scheduler.get_job(AUTO_ABSENT_JOB_ID)
    if existing is not None:
        logger.info("event=scheduler_job_exists job_id=%s", AUTO_ABSENT_JOB_ID)
        return

    trigger = CronTrigger(
        day_of_week="mon-sat",
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

    if settings.EMAIL_AUTOMATION_ENABLED and settings.EMAIL_MONTHLY_AUTOMATION_ENABLED:
        existing_monthly = scheduler.get_job(MONTHLY_EMAIL_JOB_ID)
        if existing_monthly is None:
            monthly_trigger = CronTrigger(
                day=settings.EMAIL_MONTHLY_DAY,
                hour=settings.EMAIL_MONTHLY_HOUR,
                minute=settings.EMAIL_MONTHLY_MINUTE,
                timezone=settings.SCHEDULER_TIMEZONE,
            )
            scheduler.add_job(
                monthly_report_email_job,
                trigger=monthly_trigger,
                id=MONTHLY_EMAIL_JOB_ID,
                replace_existing=False,
                coalesce=settings.SCHEDULER_COALESCE,
                max_instances=settings.SCHEDULER_MAX_INSTANCES,
                misfire_grace_time=3600,
            )
            logger.info(
                "event=scheduler_job_registered job_id=%s day=%s hour=%s minute=%s timezone=%s",
                MONTHLY_EMAIL_JOB_ID,
                settings.EMAIL_MONTHLY_DAY,
                settings.EMAIL_MONTHLY_HOUR,
                settings.EMAIL_MONTHLY_MINUTE,
                settings.SCHEDULER_TIMEZONE,
            )
