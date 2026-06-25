## 2026-06-25 — PII Logging Redaction
**Data traced:** Emails, OTPs, and Phone Numbers.
**Exposure found:** Logged in plaintext across multiple endpoints (e.g., `backend/api/auth.py`, `backend/api/users.py`, `backend/api/detection.py`, `backend/api/spam.py`).
**Fix:** Modified `backend/core/logger.py` to add `redact_pii`, a recursive `structlog` processor, which applies context-bounded regex matching for Emails, OTPs, and Phone Numbers to mask them before they reach log outputs.
**Coverage confirmed:** Verified via a manual python test (`test_patched_logger.py`) that sensitive fields are successfully masked to `[REDACTED_EMAIL]`, `[REDACTED_OTP]`, and `[REDACTED_PHONE]` in various test logging scenarios mimicking actual events, whilst avoiding general IDs and numbers. Confirmed backend imports properly.
**Still exposed elsewhere:** This only covers the `structlog` logging layer in the backend. Third-party integrations or manual exception print statements could still bypass this. Next steps should investigate structural deletion mechanisms across the database.
