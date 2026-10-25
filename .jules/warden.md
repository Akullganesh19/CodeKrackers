## 2026-10-25 — PII Redaction in Logs
**Data traced:** Email, phone numbers, and OTPs.
**Exposure found:** Plaintext logging in `backend/api/auth.py`, `backend/services/notifier.py`, `backend/services/spam_shield.py`, etc.
**Fix:** Created central `backend/core/log_filters.py` and updated `backend/core/logger.py` to use `structlog` to structurally mask emails, phones, and OTPs.
**Coverage confirmed:** Masking logic confirmed on real log formats (`user@example.com` -> `u***@example.com`, `+14155552671` -> `+1***-***-2671`).
**Still exposed elsewhere:** Other forms of PII like IP addresses or locations may still be exposed in database structures.
