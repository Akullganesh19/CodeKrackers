## 2024-05-24 — Redact PII and Auth Credentials in Core Logger
**Data traced:** User emails, E.164 phone numbers, and OTP/Password values.
**Exposure found:** Actively leaked in plaintext application and warning logs (e.g., `vas.auth`, `vas.test`, `vas.users` channels) tracking auth failures, generated OTPs, and user creation events, ultimately visible to anyone reading application logs or error tracking systems.
**Fix:** Implemented centralized structural redaction in `backend/core/logger.py` via `logging.Filter` and `structlog` processors. The logic irreversibly masks these values inline using regex across log messages, arguments, and arbitrary context fields before they reach standard output or JSON emitters.
**Coverage confirmed:** Interactively ran logging tests verifying structlog JSON and stdlib log emitters correctly masked `test@example.com` to `t***@example.com`, `+14155552671` to `+14***71`, and OTP codes `123456` to `***`.
**Still exposed elsewhere:** PII might still exist in persistent data stores like sqlite DB or caches, and long-lived exports that have not been expired or scrubbed yet. We only addressed the active active logging exposure.
