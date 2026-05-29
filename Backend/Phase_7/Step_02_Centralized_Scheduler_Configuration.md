# Step 02 - Centralized Scheduler Configuration

## Goal
Create centralized config controls for scheduling behavior and execution safety.

## Config Fields
- `SCHEDULER_ENABLED`
- `AUTO_ABSENT_HOUR` and `AUTO_ABSENT_MINUTE`
- Timezone configuration
- `AUTO_ABSENT_RETRY_LIMIT`
- `AUTO_ABSENT_BATCH_SIZE`
- Debug and observability toggles

## Strategy
- Read from environment with safe defaults
- Validate config values at startup
- Keep scheduler knobs independent from route logic

## Output
Single source of truth for scheduler runtime behavior.
