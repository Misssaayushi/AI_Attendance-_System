import smtplib

import pytest

from app.config import settings
from app.email.smtp_client import SMTPClient
from app.email.attachment_service import AttachmentService
from app.email.template_service import EmailTemplateService
from app.email.types import EmailMessagePayload, ReportEmailRequest


def test_email_template_render_daily():
    req = ReportEmailRequest(
        report_type="daily",
        report_label="All Students",
        attachment_path="dummy.xlsx",
        recipients=["admin@example.com"],
        date_label="2026-05-29",
        summary={"total_students": 120, "present": 90},
    )
    payload = EmailTemplateService.render(req)
    assert "Daily Attendance Report" in payload.subject
    assert "total_students: 120" in payload.body_text
    assert "<html>" in payload.body_html
    assert "Summary" in payload.body_html
    assert payload.recipients == ["admin@example.com"]


def test_attachment_validation_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        AttachmentService.validate_report_attachment("definitely_missing_file.xlsx")


def test_validate_email_settings_skips_when_disabled():
    original = settings.EMAIL_ENABLED
    try:
        settings.EMAIL_ENABLED = False
        settings.validate_email_settings()
    finally:
        settings.EMAIL_ENABLED = original


def test_smtp_send_with_retry_succeeds_after_one_failure(monkeypatch):
    calls = {"count": 0}

    def flaky_send_once(payload):
        calls["count"] += 1
        if calls["count"] == 1:
            raise smtplib.SMTPServerDisconnected("temporary disconnect")
        return None

    monkeypatch.setattr(SMTPClient, "send_once", flaky_send_once)
    payload = EmailMessagePayload(subject="x", body_text="y", recipients=["a@example.com"])
    attempts = SMTPClient.send_with_retry(payload, retry_limit=2, backoff_seconds=0)
    assert attempts == 2


def test_smtp_send_with_retry_non_retryable_fails_fast(monkeypatch):
    calls = {"count": 0}

    def bad_send_once(payload):
        calls["count"] += 1
        raise smtplib.SMTPAuthenticationError(535, b"auth failed")

    monkeypatch.setattr(SMTPClient, "send_once", bad_send_once)
    payload = EmailMessagePayload(subject="x", body_text="y", recipients=["a@example.com"])
    with pytest.raises(smtplib.SMTPAuthenticationError):
        SMTPClient.send_with_retry(payload, retry_limit=3, backoff_seconds=0)
    assert calls["count"] == 1
