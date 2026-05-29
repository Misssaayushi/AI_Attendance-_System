# Step 07 - Scheduling and Automation Integration Plan

## Goal
Integrate email delivery with existing automation (Phase 7 scheduler) safely.

## Integration Points
- Trigger daily report email after auto-absent completion
- Trigger monthly report email via scheduled monthly job or manual endpoint
- Reuse execution-lock semantics to avoid duplicate sends

## Safety Rules
- Send only after report file generation success
- Track per-date/per-report-type delivery status

## Output
Safe automation integration design without unstable background complexity.
