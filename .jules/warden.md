## 2026-06-20 — PII Masking in Application Logs
**Data traced:** PII data including email addresses, phone numbers, and OTP codes.
**Exposure found:** PII data was logged in plaintext via application and error logs via structlog in components such as `backend/api/users.py`, `backend/services/spam_shield.py`, and `backend/api/auth.py`.
**Fix:** Created a custom structlog processor `redact_pii` in `backend/core/logger.py` to recursively traverse log event dictionaries and automatically mask emails, phone numbers, and OTP codes with regex patterns before rendering.
**Coverage confirmed:** Wrote and ran a script to confirm that single strings and deeply nested dicts/lists containing the sensitive values are successfully masked when output to stdout.
**Still exposed elsewhere:** Future scans should verify the system's ability to delete historical data and examine PII in internal exception traces / StackInfo.
