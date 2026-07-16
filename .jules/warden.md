## 2026-07-16 — Centralized PII Redaction in Logs
**Data traced:** PII including emails, phone numbers, OTPs, SSNs, and identifier passwords.
**Exposure found:** PII leaked in plain text within backend API logs, service logs, exception messages, and structured log fields. Standard logger statements and structlog configurations lacked any redaction.
**Fix:** Created `backend/core/redaction.py` for structural masking via regex and key-based dictionary scrubing. Intercepted logging globally in `backend/core/logger.py` by applying `RedactingFormatter` to `logging.root` and inserting a `redact_structlog_processor` to the end of the `structlog` pipeline (post-exception formatting).
**Coverage confirmed:** Tested regex rules for standard formatting and context-aware OTP matching without falsely modifying timestamps. Captured structured logging output locally with missing handler replacement and verified dictionary, event message, and stack trace redaction.
**Still exposed elsewhere:** Potential leaks to third-party endpoints or database caches outside standard Python logging were not reviewed yet.
