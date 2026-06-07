# Step 06 - Stability and Soak Testing Workflow

## Goal
Validate long-runtime reliability under repeated usage.

## Stability Tests
- Extended API hit cycles
- Scheduler repeated execution validation
- DB session/connectivity resilience checks
- Excel/email workflow continuity checks

## Soak Script
- Script path:
  - `Backend/scripts/phase10_soak_test.py`
- Example command:
  - `cd Backend`
  - `python scripts/phase10_soak_test.py --base-url http://localhost:8000 --username <admin_username> --password <admin_password> --duration-seconds 120 --interval-ms 500 --date 2026-05-29 --department "Computer Science"`

## Pass Criteria (Baseline)
- Failure rate <= 5%
- Stable average latency trend
- No repeated 500-series bursts in diagnostics metrics

## Output
Repeatable soak/stability testing workflow with failure observation criteria.
