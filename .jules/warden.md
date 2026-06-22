## 2024-05-24 — Structured Logger PII Redaction
**Data traced:** Email, Phone, OTPs (codes)
**Exposure found:** Plaintext application and error logging in auth, login, and user modules. E.g., `logger.warning("LOGIN_BLOCKED account locked email=%s ip=%s", form_data.username...)` or `logger.info("SECURITY: Generated OTP for %s -> %s", otp_in.identifier, otp_code)`.
**Fix:** Created a recursive `redact_pii` processor in `backend/core/logger.py` for the structlog configuration. Added generic string redaction parsing prefixes (`phone=`, `to `) and direct structured key-value redaction masking values mapped to keys containing 'email', 'phone', 'code', or 'otp'.
**Coverage confirmed:** Ran local verification using string interpolation and structured key/value logs confirming PII was masked and timestamps/IDs were left untouched to prevent over-redaction.
**Still exposed elsewhere:** Currently unknown if exports or direct DB backups contain unencrypted data beyond the scope of this logging audit. Future investigations might check export models or DB columns.
