# Step 06 - Error Handling and Retry/Recovery Workflow

## Goal
Ensure reliable delivery under SMTP and attachment failures.

## Error Classes
- SMTP authentication failure
- SMTP connection/timeout failure
- Invalid recipient failure
- Missing attachment failure
- Duplicate email prevention lock hit

## Retry Strategy
- Bounded retries with short backoff
- Retry only transient failures
- Do not retry invalid configuration errors

## Recovery
- Persist failed attempts with reason
- Support safe manual retry via service method

## Output
Graceful failure and controlled retry model.
