# Step 04 - Auto-Absent Marking Service Implementation Plan

## Goal
Design reusable service layer for absent insertion with transaction safety.

## Service Responsibilities
- Compute unmarked students efficiently
- Create absent records in bulk-safe manner
- Reuse attendance duplicate-prevention constraints
- Return execution summary: scanned, inserted, skipped, failed

## Transaction Strategy
- Use scoped DB session per run
- Batch inserts where appropriate
- Roll back safely on critical failures

## Output
Clear implementation plan for robust absent-marking service.
