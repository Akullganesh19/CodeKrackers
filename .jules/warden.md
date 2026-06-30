## 2024-05-18 — Structlog PII Redaction Leak Fix
**Data traced:** PII (emails, phone numbers, passwords, OTPs, SSNs)
**Exposure found:** System-wide application logs were passing sensitive authentication, registration, and communication variables as plaintext kwargs to `logging.getLogger`, which subsequently routed to `structlog` without any redaction layer, exposing PII in local and container logs.
**Fix:** Created a recursive `redact_pii` custom processor in `backend.core.logger` that scrubs standard context boundary fields, nested JSON dict keys, and flat log messages using secure regex. Replaced 56 isolated instances of `logging.getLogger` with the central `structlog` factory across the `backend/` directory.
**Coverage confirmed:** Ran a local log simulation script verifying PII keys and strings within nested kwargs are completely substituted with `[REDACTED]`. Ensured string type validation exists before mutation.
**Still exposed elsewhere:** Log rotation files or downstream analytics endpoints might still have historical plaintext data, which should be purged in a separate data-scrubbing sprint.

## ⚖️ Warden: Structlog PII Redaction Leak Fix

**What:** Un-redacted sensitive string leakage in application logs
**Data classification:** PII (emails, passwords, phone numbers, OTPs)
**Exposure before:** Plaintext log files and console streams where developers logged `email=user.email` or `password=req.password` for debugging across 56 files in `backend/`.
**Fix:** Added an automated structlog pipeline processor `redact_pii` that runs centrally across all logs to sanitize sensitive strings based on field names and context boundaries. Replaced default Python loggers with this configured structlog logger.
**Verified:** Wrote a test payload that attempts to log raw OTPs, emails, and passwords, and successfully verified the output only contained `[REDACTED]`.
**Remaining gaps:** Downstream sinks (like Kibana/CloudWatch if configured) contain old historical logs that must be rotated or purged; any custom print statements not using standard logging were not covered.
