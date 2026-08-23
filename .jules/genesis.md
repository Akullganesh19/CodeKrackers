## 2024-05-24 — Add Circuit Breakers and Retries to AI Services

**Failure point found:** External calls to local Ollama API, OpenClaw Agent Gateway, and Groq Cloud LLM lacked resilience mechanisms (no automatic retries on transient errors and no circuit breaker for sustained outages).
**Why it existed:** Quick integrations assumed high availability, leading to unprotected `requests` and API client calls.
**Recovery built:** Created `backend/core/resilience.py` with `CircuitBreaker`, `with_retry_sync`, and `with_retry`. Wrapped local Ollama requests, OpenClaw agent communication, and Groq Cloud completion calls in these decorators.
**Blast radius before:** Transient network errors or brief service restarts would crash the threat analysis functions, resulting in false negatives or system hangs.
**Watch for:** Other third-party integrations (e.g., Twilio, DB, Redis) that might lack retry or circuit breaker patterns.
