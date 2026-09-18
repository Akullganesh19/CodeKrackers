## 2026-09-18 — Redact Sensitive Data from Application Logs
**Data traced:** PII (Email addresses and Phone numbers) and security secrets (OTP codes).
**Exposure found:** Logged in plaintext in the application logs via `backend/core/logger.py` and various log statements (e.g., `SECURITY: Generated OTP for...`).
**Fix:** Introduced a `PIIRedactor` custom structlog processor in `backend/core/logger.py` that intercepts all log events and applies regex-based redaction for emails, phone numbers, and 6-digit OTP codes.
**Coverage confirmed:** The structlog processor automatically applies redaction across the entire application for string inputs passed to log statements, preventing sensitive values from appearing in logs/outputs without needing to refactor every log site individually.
**Still exposed elsewhere:** Potential exposures via explicit dictionary prints or standard python `print()` statements which bypass `structlog`. Test/Seed data may still contain real-looking PII patterns. No deletion mechanism examined during this session.
