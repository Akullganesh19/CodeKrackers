## 2025-02-27 — Global Redaction of PII in Logs
**Data traced:** Email addresses and Phone numbers.
**Exposure found:** Plaintext logs across multiple endpoints (`auth`, `users`, `childlock`, `login`) where `logger.info`, `logger.warning`, and `logger.error` emit user emails and E.164 phone numbers (e.g. `LOGIN_SUCCESS email=%s`, `USER_CREATED email=%s`, `Generated OTP for %s`).
**Fix:** Created `backend/core/redact.py` with irreversible regex-based masking. Patched `backend/core/logger.py` to add `RedactingFilter` to standard root logger and `structlog_redactor` to `structlog` pipeline. This redacts PII globally.
**Coverage confirmed:** Verified redaction functions with unit tests (mock string/data substitutions via `test_redact.py` manually during session). Verified the injection into the Python root logger and structlog pipeline within `setup_logging`.
**Still exposed elsewhere:** PII might still exist in exports (e.g., CSV endpoints) or in the database unencrypted, but the active leakage into all log files (application/console/error logs) is closed structurally.
