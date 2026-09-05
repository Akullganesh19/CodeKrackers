## 2024-05-24 — Adding Resilience Decorators
**Failure point found:** External third-party API calls (Groq, Ollama, Twilio) lacked retry mechanisms and circuit breakers, leading to potential silent failures, hanging requests, or cascading failures.
**Why it existed:** Initial implementation focused on core logic without accounting for transient network or external service failures.
**Recovery built:** Implemented @CircuitBreaker and @with_retry_sync decorators in backend/core/resilience.py. Applied them to Groq, Ollama, and Twilio calls.
**Blast radius before:** Any transient API failure would immediately fail the operation (e.g., threat detection or alert sending). An API outage would repeatedly timeout on every request, degrading overall system performance.
**Watch for:** Other external HTTP requests or potentially flaky database connections.
