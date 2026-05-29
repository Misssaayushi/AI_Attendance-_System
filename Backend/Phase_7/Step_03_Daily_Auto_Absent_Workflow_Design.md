# Step 03 - Daily Auto-Absent Workflow Design

## Goal
Define deterministic daily flow executed after college closing time.

## Workflow
Scheduler Trigger (5:00 PM or configured)
-> Fetch active student roster
-> Fetch attendance records for target date
-> Identify unmarked students
-> Mark absentees in DB
-> Sync updates to monthly Excel
-> Persist execution status/log

## Safety Considerations
- Date and timezone consistency
- Idempotent absent-marking behavior
- Strict handling of empty/invalid student sets

## Output
Production-ready daily workflow contract.
