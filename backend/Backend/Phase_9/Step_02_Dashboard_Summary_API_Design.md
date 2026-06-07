# Step 02 - Dashboard Summary API Design

## Goal
Design APIs for high-level dashboard metrics with consistent response structure.

## Summary Metrics
- total_students
- present_today
- absent_today
- attendance_percentage

## API Contract
- `GET /dashboard/summary`
- Optional date and department filters
- Standardized success/data envelope

## Output
Reusable summary API specification for dashboard cards.
