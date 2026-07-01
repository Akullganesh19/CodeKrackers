## 2024-07-01 — Self-Healing API Resilience

**Failure point found:** External API calls for OTP sending (Twilio, SendGrid) and AI scanning (Groq, Ollama) were completely unprotected. They lacked retry logic for transient failures and had no circuit breakers to prevent cascading delays when dependencies went offline.

**Why it existed:** The APIs were assumed to have 100% uptime, and initial implementation prioritized happy-path functionality over edge-case error handling.

**Recovery built:**
1. `backend/core/resilience.py` introduced containing `@with_retries` (exponential backoff) and `@circuit_breaker` (fail-fast to prevent cascading delays).
2. Auth Service (`send_otp`) now isolates external calls into resilient helper functions that appropriately raise and catch exceptions, returning `503 Service Unavailable` instead of false positives when gateways fail.
3. AI Deep Scan Service and Ollama Service use these decorators to reliably handle timeouts or 500s from model endpoints, and gracefully fallback.

**Blast radius before:** Any transient glitch from Twilio/SendGrid would drop a login attempt and give the user a silent false-positive "OTP Sent" success message. If Groq went down, every message analysis request would hang or fail completely.

**Watch for:** Other external dependencies like `requests.get` or `httpx.post` calls to third-party endpoints in the analytics or legal services.
