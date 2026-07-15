## 2026-05-08 — Centralized PII Log Redaction
**Data traced:** PII (email, phone, OTP codes, identifiers, passwords)
**Exposure found:** Plaintext leakage into app and error logs via `logging` and `structlog` calls (e.g. `logger.info` capturing unmasked OTPs, emails, and full phone numbers).
**Fix:** Introduced structural redaction at the root logging level in `backend/core/logger.py` and `backend/core/redaction.py`. This masks sensitive data irreversibly in standard text logs (via custom formatter) and structlog event dictionaries (via processor). It intelligently masks portions of emails and retains non-sensitive digits (like timestamps or stack traces).
**Coverage confirmed:** Triggered simulated endpoints manually testing different variants of logs to ensure variables were successfully masked across both logging modes (`standard` text formats, and `json` outputs with `structlog`).
**Still exposed elsewhere:** This specific session only closed standard application logs. Sensitive user data (like PII in database rows or exported reports) might still lack access auditing or secure deletion capabilities, requiring separate analysis.
