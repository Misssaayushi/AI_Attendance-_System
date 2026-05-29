# Step 06 - Filtering and Query Parameter Utilities

## Goal
Provide reusable filter parsing/validation for analytics endpoints.

## Supported Filters
- date
- from_date / to_date
- department
- semester
- status (where applicable)

## Utility Behavior
- Validate date ranges
- Normalize empty filters
- Return clean filter object for service layer

## Output
Reusable filter utility layer for consistent analytics behavior.
