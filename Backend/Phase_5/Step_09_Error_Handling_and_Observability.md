# Step 09 - Error Handling and Observability

## Objective
Define robust failure handling and operational observability for attendance workflows.

## Error Handling Workflow
- Domain exceptions (StudentNotFound, DuplicateAttendance, InvalidAttendanceState)
- Validation errors mapped to 400/422
- Auth errors mapped to 401/403
- DB failures mapped to 500 with safe messages

## Observability Standards
- Structured logs for mark attempts and outcomes
- Correlation IDs/request tracing via middleware
- Success/failure counters readiness for metrics
- Minimal sensitive data logging policy

## Output of This Step
- Attendance error catalog
- HTTP mapping table
- Logging/event checklist
