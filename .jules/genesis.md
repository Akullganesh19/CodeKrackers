## 2026-08-14 — Resilient External AI Integrations
**Failure point found:** Unprotected synchronous HTTP calls to external AI services (Ollama, Groq, OpenClaw) that could cause silent failures or system hang without retries or fallback handling.
**Why it existed:** Quick integrations of LLMs via bare `requests.get`/`requests.post` without considering network fragility, rate limits, or transient timeouts.
**Recovery built:**
- Added a `CircuitBreaker` and `with_retry_sync` decorators to `backend.core.resilience`.
- Wrapped Ollama health checks and API calls with `CircuitBreaker` and Retries.
- Wrapped Groq AI calls with Retries with exponential backoff.
- Wrapped OpenClaw availability checks with `CircuitBreaker` and Retries.
**Blast radius before:** Any transient failure in Groq would fail the AI scan entirely for an SMS. If Ollama hung, the entire request could hang or fail without tripping a circuit breaker.
**Watch for:** Other `requests.get` or `requests.post` calls across the codebase (e.g. webhook receivers, external data enrichments) that should be wrapped with `CircuitBreaker` or `with_retry_sync`.
