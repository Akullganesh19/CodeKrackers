## 2026-08-12 — Structural Data Governance Fix: Redacting PII in Logs and Removing Plaintext OTPs

**Data traced:** PII (Email addresses, Phone numbers) and security tokens (OTPs).
**Exposure found:**
1. `backend/api/auth.py`, `backend/api/v1/endpoints/auth.py`, and `backend/services/notifier.py` actively logged generated 6-digit OTPs in plaintext to the application logs alongside user identifiers.
2. Emails and phone numbers were logged in plaintext throughout the application (e.g., in access logs, spam reports, anomaly detection, audit trails).
**Fix:**
1. Removed all active plaintext logging of OTP codes from the codebase, replacing them with safe messages like `SECURITY: Generated OTP for {otp_in.identifier}` or `FALLBACK SIMULATED OTP TO {phone_number}`.
2. Built an irreversible redaction layer directly into `backend/core/logger.py` (`RedactingFormatter` and `redact_dict_processor`). This structurally masks emails (`t***@example.com`) and phone numbers (`[REDACTED_PHONE:1234]`) at the root logging level, safeguarding both JSON and string log output against all future leaks of PII identifiers via logs.
**Coverage confirmed:** Ran custom tests (`test_redact11.py`) validating that structural redaction successfully targets string outputs and `structlog` JSON outputs, preventing exposure across varying schemas (like +91 98765 43210 vs 18005550199).
**Still exposed elsewhere:**
- `ChildActivityLog` in the database stores potentially sensitive phone numbers in plaintext.
- Phone numbers and identifiers might still leak into third-party integrations (e.g. sent directly to Groq/LLMs).
