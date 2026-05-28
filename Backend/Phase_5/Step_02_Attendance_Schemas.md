# Step 02 - Attendance Schemas

## Objective
Create strict request/response schemas for attendance operations.

## Planned Schemas
- AttendanceMarkRequest
- AttendanceMarkResponse
- AttendanceRecordResponse
- AttendanceListResponse (paginated)
- AttendanceFilterParams
- AttendanceSummaryResponse (analytics-ready)

## Validation Rules
- student_id required and positive
- date format ISO compliant
- status enum constrained (Present, Absent, Late)
- optional confidence score bounded (0.0 to 1.0)
- reject malformed payloads with clear messages

## Output of This Step
- Schema contract definitions
- Validation behavior matrix
- Error response map for invalid inputs
