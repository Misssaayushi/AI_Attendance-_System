from __future__ import annotations

from app.email.types import EmailMessagePayload, ReportEmailRequest


class EmailTemplateService:
    """Reusable template renderer for report emails."""

    @staticmethod
    def _subject(request: ReportEmailRequest) -> str:
        if request.report_type == "daily":
            return f"Daily Attendance Report - {request.date_label}"
        if request.report_type == "monthly":
            return f"Monthly Attendance Report - {request.date_label}"
        return f"Department Attendance Report - {request.report_label} - {request.date_label}"

    @staticmethod
    def _body_text(request: ReportEmailRequest) -> str:
        lines = [
            "Hello,",
            "",
            f"Please find attached the {request.report_type} attendance report.",
            f"Report label: {request.report_label}",
            f"Report date: {request.date_label}",
        ]
        if request.summary:
            lines.append("")
            lines.append("Summary:")
            for key, value in request.summary.items():
                lines.append(f"- {key}: {value}")
        lines.extend(["", "Regards,", "AI Attendance System"])
        return "\n".join(lines)

    @staticmethod
    def _body_html(request: ReportEmailRequest) -> str:
        summary_html = ""
        if request.summary:
            rows = "".join(
                f"<tr><td style='padding:4px 8px;border:1px solid #ddd;'>{key}</td><td style='padding:4px 8px;border:1px solid #ddd;'>{value}</td></tr>"
                for key, value in request.summary.items()
            )
            summary_html = (
                "<p><strong>Summary</strong></p>"
                "<table style='border-collapse:collapse;border:1px solid #ddd;'>"
                f"{rows}</table>"
            )

        return (
            "<html><body>"
            "<p>Hello,</p>"
            f"<p>Please find attached the <strong>{request.report_type}</strong> attendance report.</p>"
            f"<p>Report label: <strong>{request.report_label}</strong><br/>"
            f"Report date: <strong>{request.date_label}</strong></p>"
            f"{summary_html}"
            "<p>Regards,<br/>AI Attendance System</p>"
            "</body></html>"
        )

    @classmethod
    def render(cls, request: ReportEmailRequest) -> EmailMessagePayload:
        return EmailMessagePayload(
            subject=cls._subject(request),
            body_text=cls._body_text(request),
            body_html=cls._body_html(request),
            recipients=request.recipients,
        )
