# Step 10 - Testing and Debugging Workflow

## Goal
Validate correctness, reliability, and performance of dashboard analytics APIs.

## Testing Layers
- Unit tests: calculation and graph-format utilities
- Service tests: aggregate query and filter behavior
- Route tests: response structure and status validation
- Regression tests: empty datasets and invalid filters

## Performance Validation
- Measure response time for summary/trend endpoints
- Validate query counts and execution stability

## Execution Commands
- Run focused Phase 9 tests:
  - `python -m pytest Backend/app/tests/test_dashboard_routes.py -v`
- Run broader backend validation:
  - `python -m pytest Backend/app/tests/test_dashboard_routes.py Backend/app/tests/test_attendance_routes.py Backend/app/tests/test_scheduler_routes.py Backend/app/tests/test_email_workflow.py -v`

## Smoke Test Script
- Script path:
  - `Backend/scripts/phase9_smoke_test.py`
- Example usage:
  - `cd Backend`
  - `python scripts/phase9_smoke_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5 --date 2026-05-29 --department "Computer Science" --days 7`

## API Validation Checklist
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/stats/daily`
- `GET /api/v1/dashboard/stats/monthly`
- `GET /api/v1/dashboard/stats/department`
- `GET /api/v1/dashboard/graphs/weekly`
- `GET /api/v1/dashboard/graphs/monthly`
- `GET /api/v1/dashboard/graphs/department`
- `GET /api/v1/dashboard/monitoring/summary`

## Required Configuration from User Side
- Valid DB and existing student/attendance data
- Analytics config sanity:
  - `ANALYTICS_DEFAULT_TREND_DAYS`
  - `ANALYTICS_MAX_TREND_DAYS`
  - `ANALYTICS_ENABLE_PERF_METRICS`
- Auth-ready admin credentials for protected endpoints

## Output
Repeatable testing workflow for production-grade dashboard APIs.
