## 2026-05-08 — Logger Redaction
**Data traced:** PII (Email, Phone, OTP)
**Exposure found:** Application and error logs containing plaintext emails, phone numbers, and OTPs.
**Fix:** Added a structural redaction layer to `backend/core/logger.py` for both standard library logging and structlog.
**Coverage confirmed:** The redaction logic properly masks sensitive data before writing logs without modifying underlying application objects.
**Still exposed elsewhere:** Potential third-party integration points like analytics or exports, access to the database lacking fine-grained field-level access control.
