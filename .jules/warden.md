## 2026-06-26 — Logging that leaks PII
**Data traced:** Email addresses, Phone numbers, and OTP codes.
**Exposure found:** Sensitive fields logged in plaintext in application logs (e.g. `backend/api/auth.py` and `backend/api/detection.py`).
**Fix:** Created a custom `structlog` processor (`redact_pii`) in `backend/core/logger.py` to traverse log objects and redact emails (partial mask), phone numbers (full block via context), and OTPs (full block). Replaced all naive `logging.getLogger` calls with the custom `structlog` setup.
**Coverage confirmed:** Tested the regex patterns using `test_redact_cases.py` to ensure emails, phones, and OTPs matched context prefixes (`phone=`, `sender=`, `->`, etc) and redacted appropriately without mangling other data IDs. App initializes properly.
**Still exposed elsewhere:** Potential third-party APIs (like Groq) passing through raw content without pre-redaction might still capture internal context if logs from the provider are examined, though application logs are now secured.
