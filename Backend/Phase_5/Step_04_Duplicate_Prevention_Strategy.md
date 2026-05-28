# Step 04 - Duplicate Prevention Strategy

## Objective
Prevent repeated attendance marks for the same student/day and prepare idempotent behavior.

## Core Prevention Rules
- One attendance record per student per attendance date
- Optional status transition rules (for future: Present -> Late policy)
- Configurable cooldown window readiness for recognition retries

## Technical Design
- Composite uniqueness guard (student_id + date)
- Pre-insert existence check in service layer
- DB-level constraint as final safety net
- Return safe duplicate message rather than silent overwrite

## Output of This Step
- Duplicate prevention ruleset
- DB and service-level anti-duplication plan
- Edge-case handling notes
