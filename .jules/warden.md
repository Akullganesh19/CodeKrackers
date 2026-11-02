## 2025-05-08 — PII Logging Exposure
**Data traced:** Email, phone numbers, OTPs, Passwords, Identifiers
**Exposure found:** Plaintext logging in standard console/JSON logs (e.g. `logger.info("Generated OTP for user@example.com -> 123456")` or passing explicit kwargs)
**Fix:** Implemented a structlog `redact_sensitive_data` processor in `backend/core/logger.py` to recursively mask sensitive dict kwargs and regex-mask sensitive strings inside log messages.
**Coverage confirmed:** Verified logs via python test script to ensure email, phone, and OTP formats are automatically masked before emitting.
**Still exposed elsewhere:** Potential third-party integration logs not using the central structlog instance, database backups.
