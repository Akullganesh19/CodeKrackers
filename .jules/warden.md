## 2025-06-25 — PII Redaction in Logging

**Data traced:** PII (Email, Phone numbers, Identifiers, OTPs, Tokens, Passwords)
**Exposure found:** Auth endpoints actively logging plaintext OTP codes and string interpolation of identifiers. PII passing through exception tracebacks unmasked.
**Fix:** Removed plaintext OTP logging, transitioned `identifier` to structured logging keys. Created a custom `structlog` processor `redact_pii` (placed after `StackInfoRenderer()` and `format_exc_info`) that partially masks emails in strings (`j***@gmail.com`), completely masks phone numbers via Regex, and recursively scrubs any keys matching sensitive patterns (e.g. `email`, `otp`, `password`).
**Coverage confirmed:** The `redact_pii` processor traverses dicts and lists, targeting only explicit/bounded key matches (e.g., `otp`, `otp_code`) rather than substring overlaps.
**Still exposed elsewhere:** No further unredacted logs actively passing through the auth or core logging mechanisms identified in this session.
