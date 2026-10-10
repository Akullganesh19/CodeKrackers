## 2024-05-08 — Global PII Redaction in Logs
**Data traced:** Email addresses, phone numbers, and IP addresses.
**Exposure found:** Plaintext logging across multiple endpoints and services (e.g., login attempts, spam shield, honeypots, phone intel). This exposes sensitive data in application logs, which could be collected by external systems.
**Fix:** Implemented a global redaction layer in `backend/core/logger.py` using a custom `RedactFilter` for standard library logging and a `redact_structlog` processor for `structlog`. This structurally masks emails, phone numbers, and IP addresses universally without needing to patch individual log calls.
**Coverage confirmed:** Verified via a local test script (`test_patched_logger.py`) that log calls using both standard `logging` and `structlog` successfully redact the targeted fields in log messages and dictionary arguments. Ran the pytest test suite to ensure no regressions were introduced by the logger changes.
**Still exposed elsewhere:** Third-party tracking and unredacted endpoints/views may still return this data; further auditing of DB storage, exports, and analytics integrations is needed.
