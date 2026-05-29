# Step 05 - Attendance Update Pipeline

## Goal
Define safe pipeline for writing attendance into workbook cells.

## Pipeline
1. Validate incoming attendance record
2. Resolve workbook (create/open)
3. Resolve student row
4. Resolve date column
5. Apply status update with conflict rules
6. Save workbook atomically
7. Log write outcome

## Update Rules
- Prevent accidental overwrite with weaker data
- Support idempotent re-processing
- Handle duplicate/day conflicts cleanly

## Output
Reliable update mechanism for live attendance writes.
