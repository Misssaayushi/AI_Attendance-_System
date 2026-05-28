# Step 06 - Attendance APIs and Route Registration

## Objective
Define attendance API surface and integrate routes into modular backend router.

## Planned Endpoints
- POST `/attendance/mark`
- GET `/attendance`
- GET `/attendance/{attendance_id}`
- GET `/attendance/student/{student_id}`
- GET `/attendance/summary/daily`

## API Behavior
- All endpoints protected via existing authentication middleware
- Pagination for listing endpoints
- Standard response envelope for consistency
- Stable endpoint naming for frontend/AI module integration

## Output of This Step
- Endpoint contract sheet
- Route registration checklist
- Dependency injection map (db session, auth, filters)
