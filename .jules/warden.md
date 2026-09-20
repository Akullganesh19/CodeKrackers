## 2026-09-20 — PII Redaction in Logging

**Data traced:** PII (Email, Phone Numbers) and Security Tokens (OTP codes)
**Exposure found:** Log files (e.g. `USER_CREATED`, `OTP sent`, `SECURITY: Generated OTP`) exposed PII and OTPs in plaintext via `logging` and `structlog` calls.
**Fix:** Introduced an irreversible regex-based global redaction layer in `backend/core/logger.py` to mask emails, phone numbers, and OTPs for both standard Python `logging` (via a Filter) and `structlog` (via a processor).
**Coverage confirmed:** Tested string redaction, log args, structlog event dicts.
**Still exposed elsewhere:** Third-party APIs, Twilio logs (not our infra), Database records (plaintext).
