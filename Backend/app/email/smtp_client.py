from __future__ import annotations

import smtplib
import time
from email.message import EmailMessage

from app.config import settings
from app.email.types import EmailMessagePayload


class SMTPClient:
    """Lightweight SMTP sender utility for report emails."""

    @staticmethod
    def build_message(payload: EmailMessagePayload) -> EmailMessage:
        msg = EmailMessage()
        msg["Subject"] = payload.subject
        msg["From"] = settings.EMAIL_SENDER
        msg["To"] = ", ".join(payload.recipients)
        msg.set_content(payload.body_text)
        if payload.body_html:
            msg.add_alternative(payload.body_html, subtype="html")

        for attachment in payload.attachments:
            with open(attachment.file_path, "rb") as fh:
                content = fh.read()
            msg.add_attachment(
                content,
                maintype=attachment.mime_main_type,
                subtype=attachment.mime_sub_type,
                filename=attachment.file_name,
            )
        return msg

    @staticmethod
    def send_once(payload: EmailMessagePayload) -> None:
        msg = SMTPClient.build_message(payload)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT_SECONDS) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

    @staticmethod
    def is_retryable_exception(exc: Exception) -> bool:
        return isinstance(
            exc,
            (
                smtplib.SMTPServerDisconnected,
                smtplib.SMTPConnectError,
                smtplib.SMTPHeloError,
                TimeoutError,
            ),
        )

    @staticmethod
    def send_with_retry(payload: EmailMessagePayload, *, retry_limit: int, backoff_seconds: int) -> int:
        """
        Sends email with bounded retry attempts for transient SMTP failures.
        Returns the number of attempts used.
        """
        attempts = retry_limit + 1
        for attempt in range(1, attempts + 1):
            try:
                SMTPClient.send_once(payload)
                return attempt
            except Exception as exc:
                if attempt == attempts or not SMTPClient.is_retryable_exception(exc):
                    raise
                time.sleep(max(0, backoff_seconds))
        return attempts
