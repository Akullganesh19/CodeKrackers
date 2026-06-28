## 2026-06-27 — Logging PII Exposure Closed

**Data traced:** Email, Phone number, OTP, SSN, passwords
**Exposure found:** PII and sensitive data were actively being leaked into logs by numerous backend services. E.g., `EMAIL_GATEWAY_ERROR: Failed to send OTP to alice@example.com`, `OTP sent to +9876543210`, `SPAM_BLOCKED phone=+1234567890`. Kwargs to standard logger calls were also being printed. Also, the code used standard `logging.getLogger` everywhere instead of `backend.core.logger.get_logger`, entirely bypassing the `structlog` pipeline for the entire app!
**Fix:**
1. Modified `backend.core.logger.py` to include a robust custom `structlog` processor `redact_pii` which recurses through dictionaries and lists.
2. It uses strict contextual regexes (e.g. `(phone=|to\s)(\+?[1-9]\d{7,14})`) to avoid redacting legitimate, long, non-PII identifiers.
3. Updated all 50+ backend files to use `from backend.core.logger import get_logger` instead of `logging.getLogger` to ensure all logs go through the processor chain.
**Coverage confirmed:** Triggered test logs locally ensuring that `USER_CREATED`, `OTP sent`, and nested dictionary arguments are properly redacted without crashing or corrupting non-PII values. Frontend builds successfully and backend tests/flake8 verify structure.
**Still exposed elsewhere:** PII might still exist in older log files generated prior to this change. Database exports might still include PII depending on how they're generated.
