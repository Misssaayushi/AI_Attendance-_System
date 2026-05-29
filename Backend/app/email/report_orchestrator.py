from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.email.attachment_service import AttachmentService
from app.email.smtp_client import SMTPClient
from app.email.template_service import EmailTemplateService
from app.email.types import ReportEmailRequest
from app.utils.logger import logger


@dataclass
class EmailSendResult:
    success: bool
    recipients_count: int
    attachment_name: str
    error: str | None = None
    error_type: str | None = None
    attempts: int = 1


class ReportEmailOrchestrator:
    """Coordinates template rendering, attachment validation, and SMTP sending."""

    @staticmethod
    def send_report(request: ReportEmailRequest) -> EmailSendResult:
        payload = EmailTemplateService.render(request)
        attachment = AttachmentService.validate_report_attachment(request.attachment_path)
        payload.attachments = [attachment]

        try:
            attempts = SMTPClient.send_with_retry(
                payload,
                retry_limit=settings.EMAIL_RETRY_LIMIT,
                backoff_seconds=settings.EMAIL_RETRY_BACKOFF_SECONDS,
            )
            logger.info(
                "event=email_report_sent report_type=%s recipients=%s attachment=%s attempts=%s",
                request.report_type,
                len(request.recipients),
                attachment.file_name,
                attempts,
            )
            return EmailSendResult(
                success=True,
                recipients_count=len(request.recipients),
                attachment_name=attachment.file_name,
                attempts=attempts,
            )
        except Exception as exc:
            logger.exception(
                "event=email_report_failed report_type=%s recipients=%s attachment=%s",
                request.report_type,
                len(request.recipients),
                attachment.file_name,
            )
            return EmailSendResult(
                success=False,
                recipients_count=len(request.recipients),
                attachment_name=attachment.file_name,
                error=str(exc),
                error_type=type(exc).__name__,
                attempts=settings.EMAIL_RETRY_LIMIT + 1,
            )
