# Step 04 - Dynamic Date Column Management

## Goal
Auto-create and manage day columns for any target month.

## Logic
- Compute month length using calendar utilities
- Generate columns only for valid days
- Maintain deterministic column order
- Reuse existing date columns when file already exists

## Edge Cases
- Leap year February (29 days)
- Regeneration after partial workbook updates
- Locale/timezone-safe date normalization

## Output
Reusable utility to map any attendance date to the correct Excel column.
