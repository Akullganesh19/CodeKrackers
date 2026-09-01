## 2024-05-18 — External API Resilience Primitives Added

**Failure point found:** External API calls to Groq, Ollama, and Twilio lacked retry logic and circuit breakers. Transient failures would cause unhandled exceptions or immediate service degradation for callers.
**Why it existed:** The initial implementation focused on integrating external dependencies directly to enable features quickly, without architecting self-healing or defensive mechanisms against transient third-party downtime.
**Recovery built:** Created `backend/core/resilience.py` with stateful, thread-safe `@CircuitBreaker` and `@with_retry_sync` decorators. Applied these to all external HTTP requests (`requests`, `Groq`, and `Twilio` clients). Failed requests automatically retry with backoff, and sustained failures trip the circuit breaker to prevent cascading timeouts, allowing the application to gracefully degrade and fall back to local/simulated alternatives.
**Blast radius before:** A slow or failing external API could hang requests, degrade user experience, and create a poor fallback loop.
**Watch for:** Ensure new external API integrations use these resilience primitives to protect the application.
