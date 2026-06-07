# Step 10 - Testing and Debugging Workflow

## Goal
Establish confidence in Excel automation through focused backend tests.

## Testing Layers
- Unit tests: mapping/date/status utilities
- Service tests: workbook generation/update functions
- Integration tests: API endpoint to file generation flow
- Regression tests: monthly edge cases and duplicate updates

## Test Data Strategy
- Synthetic students with varied departments/semesters
- Attendance data with normal + edge cases

## Debugging Workflow
- Trace IDs in logs per export job
- Snapshot validation of generated workbooks
- Structured failure reports for quick triage

## Execution Commands
- Run focused Phase 6 tests:
  - `python -m pytest Backend/app/tests/test_excel_automation.py Backend/app/tests/test_excel_service.py -v`
- Run full backend test suite:
  - `python -m pytest Backend/app/tests -v`

## Manual API Validation (Recommended)
- Start backend:
  - `cd Backend`
  - `python run.py`
- Generate template:
  - `POST /api/v1/attendance/export/template?year=2026&month=5`
- Generate monthly workbook:
  - `POST /api/v1/attendance/export/monthly?year=2026&month=5`
- Generate department workbook:
  - `POST /api/v1/attendance/export/monthly?year=2026&month=5&department=Computer%20Science`
- Generate student workbook:
  - `POST /api/v1/attendance/export/monthly?year=2026&month=5&student_id=1`
- Sync a single attendance record:
  - `POST /api/v1/attendance/export/sync/1?year=2026&month=5`

## What to Verify in Excel Output
- Sheet names exist: `Monthly_Attendance`, `Summary`, `Metadata`
- Static student columns are fixed and ordered
- Day columns match month length (`01...31` as applicable)
- Attendance status values written correctly (`Present`, `Absent`, `Late`)
- Summary counters are consistent with records
- Metadata sheet stores selected filters

## Preconditions Required from User Side
- MySQL server running and reachable from backend
- `.env` configured with correct DB credentials and `EXPORT_DIR`
- At least one admin account for protected APIs
- Student and attendance records present for meaningful export validation
- Python environment with dependencies installed (`pip install -r Backend/requirements.txt`)

## Output
Repeatable quality checks for stable Phase 6 delivery.
