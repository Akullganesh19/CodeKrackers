## 2024-05-18 — Added circuit breakers and retries for external APIs
**Failure point found:** Unprotected third-party API calls (Groq Cloud, Local Ollama, OpenClaw Agent) in the backend services that would immediately fail upon network issues or timeouts.
**Why it existed:** Initial implementation lacked resilience and error handling for external dependencies, prioritizing feature completion over robustness.
**Recovery built:** Created `backend/core/resilience.py` with `@CircuitBreaker` and `@with_retry_sync` decorators. Extracted raw API calls into helper functions (`_call_groq_api`, `_ping_ollama`, `_invoke_ollama`, `_ping_openclaw`) and applied the decorators to implement automatic retries with exponential backoff and circuit breaking to prevent cascading failures.
**Blast radius before:** Any transient network issue or API downtime would cause the AI scanning or analysis to fail immediately, affecting all users requesting those features.
**Watch for:** Other external dependencies (e.g., Twilio, SendGrid) that may also lack retry or circuit-breaking mechanisms.
