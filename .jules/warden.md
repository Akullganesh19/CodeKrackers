## 2026-11-05 — Structural Logging PII Leak Fix
**Data traced:** PII (email, phone, OTP codes, sensitive tokens)
**Exposure found:** Plaintext in application logs and standard error streams (e.g. backend/api/auth.py generating OTPs and SMS gateways logging numbers).
**Fix:** Added a global `redact_sensitive_data` structlog processor in `backend/core/logger.py` and initialized it immediately at app startup in `backend/main.py` so all logs are safely masked.
**Coverage confirmed:** Mock tested via local python script, successfully hiding OTPs and phone numbers, masking emails contextually.
**Still exposed elsewhere:** Third-party services might still have sensitive data through separate un-logged mechanisms, to be investigated further.
