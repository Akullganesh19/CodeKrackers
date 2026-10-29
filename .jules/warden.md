## 2026-10-29 — Active Exposure in Logging Layer Fixed
**Data traced:** Email addresses, Phone numbers, OTPs, Passwords/Secrets
**Exposure found:** `backend.core.logger` logs were writing sensitive data in plaintext (e.g. from `backend.api.auth.py` and `backend.api.login.py`), making it accessible to anyone with access to application logs (stdout/stderr or structured JSON logs).
**Fix:** Modified the `structlog` configuration in `backend/core/logger.py` to add a custom processor `redact_sensitive_data`. This processor automatically masks sensitive keys (`password`, `otp`, `token`, etc.) and uses regex to partially mask emails (`j***@gmail.com`), phone numbers (`+9198***210`), and OTP codes within the `event` string.
**Coverage confirmed:** Created and ran a unit test `backend/test_logger.py` to verify that sensitive data is appropriately masked before the log is outputted.
**Still exposed elsewhere:** PII might still exist in Database backups, API Export outputs (like `/api/export/threats/csv`), and potentially external third-party API payloads (Twilio, SendGrid logs).
