"""Phase 7 Step 1: Scheduler lifecycle manager."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.scheduler.jobs import register_scheduler_jobs
from app.utils.logger import logger


_scheduler_instance: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)
    return _scheduler_instance


def initialize_scheduler() -> None:
    """
    Creates scheduler and registers jobs.
    Does not auto-start if disabled by configuration.
    """
    settings.validate_scheduler_settings()
    if not settings.SCHEDULER_ENABLED:
        logger.info("event=scheduler_disabled")
        return

    scheduler = get_scheduler()
    register_scheduler_jobs(scheduler)
    logger.info("event=scheduler_initialized")


def start_scheduler() -> None:
    """Starts scheduler if enabled and not already running."""
    if not settings.SCHEDULER_ENABLED:
        return

    scheduler = get_scheduler()
    if scheduler.running:
        logger.info("event=scheduler_start_skipped reason=already_running")
        return
    scheduler.start()
    logger.info("event=scheduler_started")


def shutdown_scheduler() -> None:
    """Stops scheduler gracefully if running."""
    global _scheduler_instance
    if _scheduler_instance is None:
        return
    if _scheduler_instance.running:
        _scheduler_instance.shutdown(wait=False)
        logger.info("event=scheduler_stopped")
    _scheduler_instance = None

