# Step 04 - Attendance Statistics Calculation Workflow

## Goal
Define deterministic calculations for attendance metrics.

## Calculation Rules
- Total = active student count in scope
- Present = records with status Present/Late in scope-date
- Absent = Total - Present (or explicit absent records when applicable)
- Percentage = (Present / Total) * 100 with zero-safe guards

## Output
Consistent calculation workflow across all analytics endpoints.
