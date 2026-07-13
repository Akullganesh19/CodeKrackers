## 2024-05-08 — Logger leaking OTP, Emails and Phone Numbers in plaintext
**Data traced:** PII (Email, Phone Numbers, OTP codes)
**Exposure found:** `backend/api/auth.py` and various other modules were emitting PII directly into the application logs through standard logging (e.g. `logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")`).
**Fix:** Created `backend/core/redaction.py` to centrally redact Emails, Phone Numbers, and OTP codes. Updated `backend/core/logger.py` to intercept both standard `logging` messages (via a custom Formatter) and `structlog` dictionaries (via a custom processor) and apply redaction recursively before writing to the stream.
**Coverage confirmed:** Tested the logger locally to ensure that plain standard log strings and structlog events have PII values successfully replaced with masked strings (e.g., `j***@gmail.com`, `***-***-2671`, `[REDACTED_OTP]`).
**Still exposed elsewhere:** Redaction only covers logging. Database state, data export, and external systems (SMS/Email gateways) remain untouched. Only standard patterns are checked; custom identifying strings outside the regex scopes might still leak.
