## 2026-05-08 — [Global Log Redaction for PII]
**Data traced:** Email addresses, phone numbers, OTPs
**Exposure found:** PII was actively leaked into application logs in plaintext (e.g., Auth failure logs with phone numbers, OTP generated logs with emails/OTPs).
**Fix:** Implemented a centralized `RedactingFormatter` for standard `logging` and a `redact_structlog` processor for `structlog` in `backend/core/logger.py`. Regex rules scrub emails (masking to `a***@example.com`), phone numbers (masking to `***-***-1234`), and OTPs before they reach stdout or log files.
**Coverage confirmed:** Created a test script to simulate standard and structlog events containing emails, phones, and OTPs. Verified the mask format appears correctly instead of the actual data.
**Still exposed elsewhere:** This redaction only targets the standard logging pipeline. Raw error stack traces sent to users in some endpoints or direct third-party analytics could still potentially contain PII, requiring specific endpoint scrutiny.
