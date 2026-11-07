## 2026-11-06 — Structural Log Redaction for PII and Secrets
**Data traced:** PII (emails, phone numbers) and Secrets (passwords, OTPs, tokens, SSNs).
**Exposure found:** Sensitive fields (like OTPs for users) logged in plaintext in application logs (e.g., `logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")`).
**Fix:** Created a `redact_sensitive_data` structlog processor in `backend/core/logger.py` that irreversibly masks sensitive fields globally across all structlog logs, both in the positional `event` string and the key-value kwargs `event_dict`.
**Coverage confirmed:** Triggered local test script with simulated sensitive log messages and verified that structlog outputs redacted values (e.g. `t***@example.com` and `[REDACTED]`).
**Still exposed elsewhere:** Potential third-party APIs (e.g., Groq / openclaw) may receive sensitive text transcripts. Database and caching layers remain unredacted; PII fields in `User` and `Blacklist` may be directly accessible via direct DB read access.
