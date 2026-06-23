## 2026-06-22 — [Logger Plaintext Leakage]
**Data traced:** PII (Email addresses, Phone numbers) and Auth Secrets (OTPs).
**Exposure found:** Plaintext logs across the backend application (e.g., `backend/api/v1/endpoints/auth.py`, `backend/services/spam_shield.py`), visible in stdout error and application logs.
**Fix:** Created a custom `structlog` redaction processor `redact_pii` in `backend/core/logger.py`. It recursively searches `event_dict` and applies context-bounded regex to mask sensitive information irreversibly (replacing them with `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_OTP]`).
**Coverage confirmed:** Tested string logs and dictionary logs emitting simulated logs matching prior application formats and verified via stdout inspection.
**Still exposed elsewhere:** This currently covers the application's logging mechanism and handles active exposures, but data export features or specific third-party analytics not going through standard logging were not reviewed during this session.
