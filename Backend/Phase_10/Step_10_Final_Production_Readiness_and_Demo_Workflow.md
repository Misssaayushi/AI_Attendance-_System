# Step 10 - Final Production-Readiness and Demo Workflow

## Goal
Define final checklist to validate backend is demo-ready and stable.

## Final Checks
- API contract consistency
- Error and auth behavior verification
- Scheduler/email/excel/analytics end-to-end validation
- Performance spot-checks
- Monitoring and diagnostics verification

## Execution Commands
- Run focused diagnostics tests:
  - `python -m pytest Backend/app/tests/test_diagnostics_routes.py -v`
- Run Phase 10 stability subset:
  - `python -m pytest Backend/app/tests/test_diagnostics_routes.py Backend/app/tests/test_dashboard_routes.py Backend/app/tests/test_scheduler_routes.py Backend/app/tests/test_email_workflow.py -v`
- Run complete Phase 10 validation matrix:
  - `cd Backend`
  - `python scripts/phase10_validation_runner.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --department "Computer Science" --days 7`
- Run complete matrix including soak:
  - `cd Backend`
  - `python scripts/phase10_validation_runner.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --department "Computer Science" --days 7 --run-soak --soak-seconds 120 --soak-interval-ms 500`

## Smoke Test Script
- Script path:
  - `Backend/scripts/phase10_smoke_test.py`
- Example usage:
  - `cd Backend`
  - `python scripts/phase10_smoke_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --department \"Computer Science\" --days 7`

## Final Validation Runner
- Script path:
  - `Backend/scripts/phase10_validation_runner.py`
- What it validates:
  - Core backend API test matrix (auth, student, attendance, analytics, diagnostics, scheduler, email)
  - API-level smoke test against running server
  - Optional soak test for short runtime stability check
- Result:
  - Prints `Status: PASSED` when demo-readiness checks pass
  - Prints `Status: FAILED` with failed step names if any part fails

## Output
End-to-end production-readiness workflow and final demo validation checklist.
