# Step 06 - Excel Synchronization Workflow for Auto-Absent

## Goal
Synchronize absent auto-marking updates into monthly Excel files reliably.

## Sync Steps
- Resolve monthly workbook for run date
- Resolve student row and date column mappings
- Write `Absent` status without overriding stronger existing values
- Save workbook atomically and log sync summary

## Consistency Requirements
- DB is source of truth
- Excel sync failures logged and recoverable
- Support replay mechanism for missed Excel sync

## Output
Safe DB-to-Excel synchronization workflow for scheduler runs.
