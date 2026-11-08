## 2025-05-08 — Logger PII Leak Redaction
**Data traced:** Email addresses and Phone numbers.
**Exposure found:** PII is logged in plaintext directly into application logs, e.g. `logger.info("USER_CREATED email=%s ...", user.email)` and `logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")`.
**Fix:** Introduced structural PII redaction by implementing custom structlog processors for both keyword arguments and positional message matching using regexes.
**Coverage confirmed:** The structlog logger now sanitizes PII (emails, phone numbers, and OTPs) from the `event` string across all logging outputs.
**Still exposed elsewhere:** Phone numbers may still be stored in the DB without adequate encryption at rest; some database fields (like `threat.source_number`) may remain unmasked.
