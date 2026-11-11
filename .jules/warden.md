## 2025-05-08 — Redacted active PII exposure in application logs
**Data traced:** PII (emails, phone numbers, passwords, OTPs)
**Exposure found:** Plain-text logging in stdout via structlog throughout multiple services (auth, users, intel, notifier). Explicit print statement of OTP in notifier.py.
**Fix:** Created and inserted a structlog custom processor (`redact_pii_processor`) to irreversibly mask sensitive keys in `event_dict` and regex match emails/phones in `event` strings. Removed raw `print` of OTP.
**Coverage confirmed:** Tested the logger output manually to verify emails and phones are correctly masked across kwargs and event string interpolations. Confirmed no functionality is broken via tests.
**Still exposed elsewhere:** PII might still exist in some database records or older log files which were not purged.
