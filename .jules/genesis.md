## 2024-05-19 — Protective Shields for External APIs (Twilio, Groq, Ollama)
**Failure point found:**
1. `backend/services/notifier.py` Twilio API calls (`send_otp` and `send_threat_alert`) lacked retry logic, causing hard failures on transient network issues.
2. `backend/services/ai_deep_scan.py` (Groq API) and `backend/services/ollama_scan.py` (Local Ollama API) lacked circuit breakers and retries, leading to potential cascading failures, blocking timeouts, and resource exhaustion if the AI services went offline or experienced high latency.

**Why it existed:** The APIs were implemented using standard blocking HTTP requests without wrapping them in resilience patterns like exponential backoff or circuit breaking.

**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retries` and `@circuit_breaker` (and async equivalents).
2. Applied `@with_retries` to `send_otp` and `send_threat_alert` to gracefully handle transient SMS delivery failures without blocking the user.
3. Applied `@circuit_breaker` and `@with_retries` to `ollama_deep_scan` and `_call_groq` to fail fast with a fallback response if the AI models become unavailable, protecting the system from hanging indefinitely on external dependencies.

**Blast radius before:** High. A transient Twilio failure would block users from authenticating (OTP) or receiving critical real-time threat alerts. AI service downtime would hang the main backend request processing and potentially crash workers.

**Watch for:** Other external HTTP integrations (e.g., webhook processing, external data lookups) that might still be using unprotected blocking requests.
