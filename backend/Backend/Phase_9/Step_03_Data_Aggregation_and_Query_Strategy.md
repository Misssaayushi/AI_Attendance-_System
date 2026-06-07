# Step 03 - Data Aggregation and Query Strategy

## Goal
Implement efficient aggregation patterns for attendance analytics.

## Query Principles
- Prefer grouped SQL aggregates over row-by-row processing
- Avoid N+1 query patterns
- Use date-scoped and department-scoped filters early in query

## Aggregations
- Daily presence/absence counts
- Department-wise attendance percentages
- Date-series counts for trend APIs

## Output
Scalable repository/query strategy for analytics workloads.
