## 2024-05-24 — Adding Circuit Breakers and Retries

**Failure point found:** External APIs (Groq, Twilio, SendGrid, Ollama) could fail silently, hang due to no configured timeouts correctly handling HTTP retries, or cause a cascading failure throughout the system since they were directly invoked in synchronous/asynchronous paths without protection.

**Why it existed:** The code initially lacked robustness for external calls, focusing more on happy-path execution for AI scans and notifications.

**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retries` (exponential backoff) and `@circuit_breaker` decorators.
2. Refactored `backend/services/ollama_scan.py`, `backend/services/ai_deep_scan.py`, `backend/services/notifier.py`, and `backend/api/auth.py` to wrap external API calls with these decorators.
3. Catch blocks now gracefully handle failures (e.g., returning fallback scores of 0.0 or bypassing notification errors).

**Blast radius before:** A single external dependency outage (like Groq or Twilio) could result in unhandled exceptions bubbling up to user-facing endpoints, resulting in 500 errors and degraded user experience during authentication or scanning.

**Watch for:** Other areas of the codebase that make external calls (e.g., honeypot.is API, Cybercrime portal API) that might need similar resilience applied in the future.
