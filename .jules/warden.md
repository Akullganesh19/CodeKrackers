## 2026-06-21 — Logger PII Leakage Fixed
**Data traced:** Email addresses, phone numbers, and OTP codes.
**Exposure found:** PII was logged in plaintext via application and error logs across multiple services (`backend/services/phone_intel.py`, `backend/services/spam_shield.py`, `backend/services/notifier.py`, `backend/api/users.py`, `backend/api/spam.py`, `backend/api/auth.py`).
**Fix:** Modified `backend/core/logger.py` to use a custom `structlog` processor (`redact_pii`) that automatically intercepts and redacts emails, phone numbers, and OTP codes via Regex matching before they are written to the logs.
**Coverage confirmed:** Ran custom tests confirming structured event dictionaries successfully redacted emails and phones to masks, without disrupting non-PII structures. Redaction occurs uniformly at the logging layer rather than the individual call sites.
**Still exposed elsewhere:** PII might still exist in older log files generated prior to the deployment of this fix, or within the database instances directly.
