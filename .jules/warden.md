## 2023-10-24 — [Global Log Redaction]
**Data traced:** Email, Phone (E.164), OTPs
**Exposure found:** Active exposure in authentication and user logs across the application (e.g., `logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")`, `logger.info("USER_CREATED email=%s role=%s", user.email, user.role.value)`).
**Fix:** Implemented a global structural log redaction by creating a standard library `logging.Filter` and a custom `structlog` processor, replacing emails, phones, and OTPs with safely masked variants (`***@domain`, `[REDACTED_PHONE]`, `[REDACTED_OTP]`). These were applied to the root logger in `setup_logging`.
**Coverage confirmed:** Confirmed that directly logged PII using stdlib loggers and structlog loggers is redacted properly before hitting stdout/stderr via automated test scripts.
**Still exposed elsewhere:** PII might still exist in non-logging external services, unredacted DB entries, or manual string printing outside the logging mechanism.
