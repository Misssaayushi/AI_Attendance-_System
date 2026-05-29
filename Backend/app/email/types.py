from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ReportType = Literal["daily", "monthly", "department"]


@dataclass
class EmailAttachment:
    file_path: str
    file_name: str
    mime_main_type: str = "application"
    mime_sub_type: str = "vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@dataclass
class EmailMessagePayload:
    subject: str
    body_text: str
    recipients: list[str]
    body_html: str | None = None
    attachments: list[EmailAttachment] = field(default_factory=list)


@dataclass
class ReportEmailRequest:
    report_type: ReportType
    report_label: str
    attachment_path: str
    recipients: list[str]
    date_label: str
    summary: dict | None = None

