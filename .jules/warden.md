## 2026-07-11 — Active PII Exposure in Application Logs

**Data traced:** Email, Phone Number, OTP Code (Sensitive authentication and contact data)
**Exposure found:** Log files across standard python `logging` and `structlog` loggers. For example, `backend/api/auth.py` and `backend/services/spam_shield.py` logged users' email addresses, phone numbers, and OTP codes in plaintext directly to logs (e.g., `logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")`).
**Fix:** Created a centralized redaction utility in `backend/core/redaction.py`. Hooked it structurally into `backend/core/logger.py` via a custom `PIIRedactingFormatter` for the standard `logging` module and a `redact_processor` structlog processor, securing logs globally from leaking PII.
**Coverage confirmed:** I verified that standard loggers outputting to `sys.stdout` and `structlog` loggers have PII successfully masked into formats like `j***@gmail.com`, `+*-***-***-4567`, and `[REDACTED OTP]`.
**Still exposed elsewhere:** This session primarily fixes PII leaks in standard system logs. Other possible data leakage like the contents of `backend/data/feature_log.jsonl` or third-party webhooks need to be investigated separately. Exports generated in `backend/api/export.py` include raw data.
