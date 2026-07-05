## 2026-07-05 — PII Redaction in Logs
**Data traced:** PII (emails, phone numbers, OTPs, SSNs)
**Exposure found:** Plaintext leakage in application, error logs, and exception tracebacks (e.g. `LOGIN_FAILED`, `SECURITY: Generated OTP`, `SMS_GATEWAY_ERROR`).
**Fix:** Re-implemented the `redact_pii` processor in `backend/core/logger.py`. The processor recursively masks sensitive structured kwargs and regex-redacts string payloads and exception traces by being placed after `format_exc_info`.
**Coverage confirmed:** Tested the `redact_pii` structlog processor via a test script to ensure emails, phones, SSNs, and OTPs were masked and exception payloads were filtered. Successfully verified compilation and execution of `backend/core/logger.py`.
**Still exposed elsewhere:** PII might still exist in older raw `.log` files, backups, or potentially third party error trackers if they capture raw locals bypassing the structlog processing layer.
