from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Integer, String, UniqueConstraint

from app.models.student import Base


class SchedulerExecution(Base):
    __tablename__ = "scheduler_executions"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(100), nullable=False, index=True)
    run_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="running")  # running, success, partial, failed
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime, nullable=True)
    total_students = Column(Integer, nullable=True)
    already_marked = Column(Integer, nullable=True)
    auto_absent_marked = Column(Integer, nullable=True)
    duplicate_skipped = Column(Integer, nullable=True)
    excel_synced = Column(Integer, nullable=True)
    attempt_count = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("job_name", "run_date", name="uq_scheduler_job_run_date"),
    )
