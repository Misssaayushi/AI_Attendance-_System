# Step 10 - Testing and Debugging Workflow

## Goal
Validate scheduler reliability, idempotency, and synchronization quality.

## Testing Layers
- Unit tests for absent-identification and lock logic
- Service tests for auto-marking transaction behavior
- Integration tests for scheduler-triggered end-to-end runs
- Regression tests for duplicate prevention and reruns

## Runtime Validation
- Simulate scheduled execution for target dates
- Validate DB writes and Excel outputs
- Verify logs and execution history records

## Long-Run Stability
- Repeated daily-run simulation
- Failure injection tests (DB/Excel exceptions)
- Recovery and retry behavior verification

## Execution Commands
- Run focused Phase 7 tests:
  - `python -m pytest Backend/app/tests/test_scheduler_setup.py Backend/app/tests/test_auto_absent_service.py Backend/app/tests/test_scheduler_routes.py -v`
- Run full backend tests:
  - `python -m pytest Backend/app/tests -v`

## API Smoke Test Script
- Script path:
  - `Backend/scripts/phase7_smoke_test.py`
- Example usage:
  - `cd Backend`
  - `python scripts/phase7_smoke_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --year 2026 --month 5`

## What to Validate
- `GET /api/v1/attendance/automation/executions` returns execution-history rows
- `GET /api/v1/attendance/automation/summary` returns aggregate scheduler metrics
- Auto-absent runs are not duplicated after successful completion for same date
- Retry attempts are visible in logs/attempt counters on transient failures
- Excel sync count aligns with successfully inserted absent records

## Required Environment Inputs
- Scheduler config in `.env`:
  - `SCHEDULER_ENABLED=true`
  - `SCHEDULER_TIMEZONE=Asia/Kolkata`
  - `AUTO_ABSENT_HOUR=17`
  - `AUTO_ABSENT_MINUTE=0`
  - `AUTO_ABSENT_RETRY_LIMIT=2`
  - `AUTO_ABSENT_BATCH_SIZE=1000`
- Valid DB connection and existing student records
- Admin credentials for authenticated route tests

## Output
Repeatable validation workflow for production-grade scheduler automation.
