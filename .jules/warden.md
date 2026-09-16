## 2026-05-08 — Close PII Leak in Logs

**Data traced:** Email addresses and Phone numbers.
**Exposure found:** Currently logged in plaintext throughout the application (e.g. `USER_CREATED email=admin@vas.com`, `OTP sent to +12025550123`). This includes both `logging` and `structlog` loggers.
**Fix:** Created redaction logic (irreversible partial masking) and applied it fundamentally inside `backend/core/logger.py` to intercept and mask both standard library logs via a `logging.Filter` and structured logs via a custom `structlog` processor. Masking format used is `u***@domain.com` for emails, and masking the last 4 digits for phone numbers (e.g., `+1415555****`).
**Coverage confirmed:** Tested the `logging.Filter` and `structlog` processors and verified they correctly mask standard and structlog events containing PII, even when formatted with kwargs.
**Still exposed elsewhere:**
- Sensitive user data (like phone numbers and possibly raw content) could be exported by admins without reduction via CSV/JSON (e.g., `/api/v1/admin/export-users` honeypot implies export functions exist, and `/api/export/threats/csv` exports raw threats).
- Test databases or analytic systems may contain unsanitized sensitive information.
