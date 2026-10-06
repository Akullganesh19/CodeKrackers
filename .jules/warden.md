## 2026-10-06 — Structural PII Logger Exposure Closed
**Data traced:** Emails, Phone Numbers, OTPs
**Exposure found:** Logged in plaintext across numerous backend files using string formatting with standard `logging.info(...)` bypassing the unconfigured `structlog`. Simulated OTPs were printed directly to stdout via `print`.
**Fix:** Created a custom regex-based `PIIFilter` and `PIIRedactor` dynamically attached to standard `logging.root.handlers` in `backend/core/logger.py`, overriding string args. Attached the equivalent filter as a processor to `structlog`. Deleted the stdout `print` in `notifier.py`.
**Coverage confirmed:** Ran manual scripts verifying emails are truncated (f***@example.com), phones are masked (***-***-3210), and OTP tokens are replaced with [REDACTED], verifying both standard logging and structlog data paths.
**Still exposed elsewhere:** Potential third-party integration points passing unredacted PII in URL parameters or exception stack traces not natively handled by structlog's exc formatter.
