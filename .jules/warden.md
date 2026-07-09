## 2026-05-08 — Centralized PII Redaction in Logging

**Data traced:** PII including emails, phone numbers, and OTPs (One Time Passwords).
**Exposure found:** Sensitive fields were logged in plaintext in application logs (e.g., in `backend/api/auth.py`, `backend/services/spam_shield.py`, and `backend/api/users.py`) through the Python standard logger and Structlog. If intercepted or ingested into a centralized log management system, these pieces of data create a serious risk of unauthorized access to user accounts, SMS spoofing, and deanonymization.
**Fix:** Created `backend/core/redaction.py` to house regex patterns and redaction logic for emails, phone numbers, and explicit OTP formats. Updated `backend/core/logger.py` to integrate a custom standard `logging.Formatter` and a `structlog` processor to automatically scan and redact these pieces of information before they are outputted.
**Coverage confirmed:** Tested the `redact_pii` utility locally to ensure it gracefully replaces sensitive data with asterisks while maintaining context (e.g., "john.doe@example.com" -> "j***e@example.com").
**Still exposed elsewhere:** PII might still exist in legacy database tables or backups. We also need to evaluate if our error-reporting systems (e.g., Sentry, if we adopt one) will capture exceptions directly bypassing our custom formatter, which requires a custom event scrubber in their SDK.
