## 2025-02-28 — PII Leakage in Application Logs
**Data traced:** PII fields (`email`, `phone`, `otp`, `ssn`, `password`, `card_number`, `phone_number`)
**Exposure found:** Plaintext logs via `logger.info`, `logger.error`, and `logger.warning` in multiple backend services and API endpoints.
**Fix:** Implemented a `redact_pii` custom processor in `backend/core/logger.py` that recursively masks PII data in string values based on regex context boundaries and fully redacts exact kwarg matches for sensitive dictionary keys.
**Coverage confirmed:** Tested string masking (including context matching) and dictionary redaction logic through a standalone script, and verified correct structlog processor placement just after `format_exc_info`.
**Still exposed elsewhere:** Currently unknown. This prevents application logging of these specific types, but logs in third-party services or integrations, if any exist outside standard logger configuration, would require separate verification.
