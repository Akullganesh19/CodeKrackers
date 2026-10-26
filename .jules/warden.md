## 2024-10-26 — PII Leak in Logs Fixed
**Data traced:** Email addresses, Phone numbers, OTP codes, Passwords
**Exposure found:** Application logs using `structlog` via `backend/core/logger.py` were capturing plaintext OTPs (from Twilio SMS fallback and SendGrid failures), emails (user creation), phones (spam blocking), and passwords (login failure payloads).
**Fix:** Added a custom structlog processor `redact_sensitive_data` to `backend/core/logger.py` that intercepts the event dictionary and applies irreversible regex redaction to emails (masking center), phones (masking first 6 digits), OTPs (masking code), and passwords.
**Coverage confirmed:** Tested the logger with dummy data to verify redactions trigger on event messages and kwargs seamlessly.
**Still exposed elsewhere:** Potential frontend debug logs or third-party analytical exports not investigated in this pass.
