# Step 10 - Testing and Debugging Workflow

## Goal
Validate reliability of email report delivery and attachment workflows.

## Testing Layers
- Unit tests: template rendering, attachment validation, recipient parsing
- Service tests: email send success/failure/retry logic
- Integration tests: report generation + attachment + email flow
- Regression tests: duplicate-delivery prevention and retry boundaries

## Failure Simulation
- SMTP auth failure
- SMTP timeout
- Missing attachment
- Invalid recipient address

## Execution Commands
- Run focused Phase 8 tests:
  - `python -m pytest Backend/app/tests/test_email_setup.py Backend/app/tests/test_email_workflow.py -v`
- Run broader automation tests:
  - `python -m pytest Backend/app/tests/test_scheduler_setup.py Backend/app/tests/test_scheduler_routes.py Backend/app/tests/test_email_setup.py Backend/app/tests/test_email_workflow.py -v`

## Smoke Test Script
- Script path:
  - `Backend/scripts/phase8_smoke_test.py`
- Example usage:
  - `cd Backend`
  - `python scripts/phase8_smoke_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --recipient-group admin`
- Optional force resend:
  - `python scripts/phase8_smoke_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --recipient-group admin --force-send`

## API Validation Checklist
- `POST /api/v1/attendance/reports/email/monthly`
  - Validates report generation + attachment + send flow
- `POST /api/v1/attendance/reports/email/daily`
  - Validates daily report send flow
- `GET /api/v1/attendance/reports/email/deliveries`
  - Validates email delivery audit history
- `GET /api/v1/attendance/reports/email/summary`
  - Validates delivery summary metrics

## Required Configuration from User Side
- `EMAIL_ENABLED=true`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `EMAIL_SENDER`
- `EMAIL_ADMIN_RECIPIENTS` and/or `EMAIL_FACULTY_RECIPIENTS`
- `EMAIL_RETRY_LIMIT`, `EMAIL_RETRY_BACKOFF_SECONDS`
- Optional scheduler integration:
  - `EMAIL_AUTOMATION_ENABLED=true`
  - `EMAIL_MONTHLY_AUTOMATION_ENABLED=true`
  - `EMAIL_MONTHLY_DAY`, `EMAIL_MONTHLY_HOUR`, `EMAIL_MONTHLY_MINUTE`
- Ensure `EXPORT_DIR` points to writable directory for report files

## Validation Checklist
- Correct subject/body and recipient group
- Correct attachment and file metadata
- Accurate delivery status tracking and logs

## Output
Repeatable testing workflow for production-grade email automation.
