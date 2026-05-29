# Step 03 - Row and Column Mapping Strategy

## Goal
Create deterministic row/column mapping between database entities and Excel cells.

## Row Mapping
- One row per student
- Stable row ordering by roll number or student_id
- Row index lookup map for fast updates

## Column Mapping
- Static metadata columns at fixed indices
- Date columns derived from month calendar
- Status encoding strategy (`P`, `A`, `L` or full text)

## Data Contracts
- Student key for idempotent updates
- Date key normalized to `YYYY-MM-DD`

## Output
A formal mapping matrix to avoid mismatched writes.
