# Step 02 - Centralized Email Configuration and Security

## Goal
Create secure, environment-driven SMTP and recipient configuration.

## Config Fields
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD
- SMTP_USE_TLS
- EMAIL_SENDER
- EMAIL_ADMIN_RECIPIENTS
- EMAIL_FACULTY_RECIPIENTS
- EMAIL_RETRY_LIMIT
- EMAIL_TIMEOUT_SECONDS

## Security Rules
- No hardcoded credentials
- Validate config on startup
- Restrict sensitive values from logs

## Output
Secure and centralized email configuration blueprint.
