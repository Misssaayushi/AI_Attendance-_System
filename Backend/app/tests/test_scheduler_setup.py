from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.scheduler.jobs import AUTO_ABSENT_JOB_ID, register_scheduler_jobs


def test_scheduler_job_registration_is_idempotent():
    scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)
    register_scheduler_jobs(scheduler)
    register_scheduler_jobs(scheduler)
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == AUTO_ABSENT_JOB_ID


def test_validate_scheduler_settings_accepts_defaults():
    settings.validate_scheduler_settings()

