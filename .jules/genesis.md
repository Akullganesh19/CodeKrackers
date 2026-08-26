## 2024-08-26 — Resilient API Communication
**Failure point found:** External API requests (Groq, Ollama, Twilio, OpenClaw) had no retry mechanisms or circuit breakers, making the system prone to crashes and hanging if endpoints experienced transient failures.
**Why it existed:** Initially developed as a hackathon prototype, relying on happy path execution without robust distributed systems failure handling.
**Recovery built:** Created a central `backend.core.resilience` module featuring `@CircuitBreaker` and `@with_retry_sync`/`@with_retry` decorators. These are wrapped around outbound helper functions for Ollama, Groq, Twilio, and OpenClaw at the global module scope to persist state.
**Blast radius before:** Any external timeout or 500 error would directly fail operations, preventing SMS analysis, OTP sending, or agent activation.
**Watch for:** Other outbound HTTP integrations (like webhook receivers or future external API dependencies) being added without these resilience decorators.
