## 2026-06-26 — PII Logging Exposure Closed
**Data traced:** Email, Phone Number, OTPs
**Exposure found:** Plaintext logging of these sensitive fields in application logs (specifically via `backend/api/auth.py` and potentially others) using structlog.
**Fix:** Implemented and added a `redact_pii` structlog processor in `backend/core/logger.py` that utilizes context boundary regexes to selectively redact emails, phones, and OTPs while leaving other content intact. It fully redacts structured kwargs when their keys match sensitive keywords.
**Coverage confirmed:** Tested the `redact_pii` processor locally, confirming string replacements and dictionary scrubbing work as intended, and validated the integration within `structlog` setup successfully scrubs test logs.
**Still exposed elsewhere:** This addresses application logs going through structlog. However, data persistence layer or standard `print`s may still expose some data, which is out of scope for this specific structured logging patch.
