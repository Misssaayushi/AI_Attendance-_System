from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.email.types import EmailAttachment


class AttachmentService:
    """Validates and normalizes report attachment inputs."""

    ALLOWED_SUFFIXES = {".xlsx"}

    @classmethod
    def validate_report_attachment(cls, file_path: str) -> EmailAttachment:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")
        if not path.is_file():
            raise ValueError("Attachment path must point to a file")
        if path.suffix.lower() not in cls.ALLOWED_SUFFIXES:
            raise ValueError("Unsupported attachment format. Expected .xlsx")
        return EmailAttachment(file_path=str(path), file_name=path.name)

    @classmethod
    def resolve_from_export_dir(cls, file_name: str) -> EmailAttachment:
        base = Path(settings.EXPORT_DIR)
        return cls.validate_report_attachment(str(base / file_name))
