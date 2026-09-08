## 2024-09-08 — Unprotected External API Calls
**Failure point found:** Multiple third-party integrations (Twilio, Groq, Ollama, OpenClaw, Honeypot.is) used raw `requests.get/post` and `httpx.get` without retry mechanisms, timeouts, or circuit breakers.
**Why it existed:** Quick implementation for hackathon/initial prototype.
**Recovery built:** Built robust decorators (`@with_retry_sync`, `@with_retry`, `@CircuitBreaker`) in `backend/core/resilience.py` and wrapped all external API calls with them.
**Blast radius before:** Any temporary network hiccup or API rate limit caused 500 errors or missed alerts/OTPs for users. A down external service could cause cascading failures and unresponsive endpoints.
**Watch for:** Other places where external systems are called.
