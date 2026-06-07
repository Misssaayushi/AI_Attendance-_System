from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Integer, String, UniqueConstraint

from app.models.student import Base


class EmailDelivery(Base):
    __tablename__ = "email_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(30), nullable=False, index=True)  # daily, monthly, department
    report_date = Column(Date, nullable=False, index=True)
    recipient_group = Column(String(20), nullable=False, index=True)
    report_label = Column(String(120), nullable=False, default="all_students")
    status = Column(String(20), nullable=False, default="running")  # running, success, failed, skipped
    attempts = Column(Integer, nullable=True, default=1)
    recipients_count = Column(Integer, nullable=True)
    attachment_name = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(String(500), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "report_type",
            "report_date",
            "recipient_group",
            "report_label",
            name="uq_email_delivery_report_scope",
        ),
    )

