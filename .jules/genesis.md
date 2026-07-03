## 2024-07-03 — Resilient External Integrations
**Failure point found:** External API calls to Groq, Ollama, and Twilio were lacking self-healing mechanisms and could cause cascading failures or silent hangs. They only relied on basic try-catch without active recovery.
**Why it existed:** The system was focused on feature delivery and assumed high availability of third-party dependencies.
**Recovery built:** Created `@circuit_breaker` and `@with_retries` decorators in `backend/core/resilience.py`. Applied these to `_make_ollama_request`, `_make_groq_request`, and `_send_twilio_message`. The circuit breaker tracks consecutive failures and transitions to an OPEN state, fast-failing and protecting downstream systems, and a retry mechanism attempts to heal transient issues.
**Blast radius before:** Any temporary API blip would hard-fail a request; prolonged outages would cause application threads to block or overwhelm upstream resources.
**Watch for:** Other unprotected network requests in new features (e.g. database connections, other external APIs). Ensure decorators raise exceptions so the circuit breaker functions properly.
