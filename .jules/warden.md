## 2025-05-08 — Logger PII Exposure

**Data traced:** Email addresses, Phone numbers, OTP codes
**Exposure found:** Plaintext logging in application and error logs, especially in authentication (`backend/api/auth.py`, `backend/services/notifier.py`, `backend/api/v1/endpoints/auth.py`) and spam/threat handling (`backend/services/spam_shield.py`, `backend/services/phone_intel.py`, `backend/api/spam.py`, `backend/api/users.py`, `backend/api/blacklist.py`).
**Fix:** Introduced a structlog processor in `backend/core/logger.py` for comprehensive, structural PII redaction of `email`, `phone`, `otp`, `identifier` and `password` inside structured logs (kwargs) and raw event strings.
**Coverage confirmed:** Tested regex string manipulation and structlog `redact_pii` processor masking. Verified masking functions `mask_email` and `mask_phone` successfully apply.
**Still exposed elsewhere:** Potential third party gateways such as Twilio or SendGrid logging externally (out of scope for application logs).
