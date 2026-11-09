## 2026-05-18 — PII and Secrets Leakage in Logs
**Data traced:** OTP codes, passwords, emails, and phone numbers.
**Exposure found:** Plaintext logs in application logs via structlog, including explicit OTPs and sensitive fields passed as keyword arguments.
**Fix:** Introduced a structlog processor in `backend/core/logger.py` to recursively mask sensitive dictionary keys (`password`, `otp`, `token`, etc) in the `event_dict` and explicitly redact matching sensitive regex patterns (like OTP send logs) in the main `event` string.
**Coverage confirmed:** Tested regex and structlog filter locally ensuring all common leaks are replaced with `***`.
**Still exposed elsewhere:** Currently only covering log output. Application state storage of active tokens and old session records may still persist and will need future audit.
