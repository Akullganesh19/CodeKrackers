## 2025-06-25 — API Circuit Breakers & Auto-Retries
**Failure point found:** Fragile external API calls (Groq, Ollama, OpenClaw, SendGrid, Twilio) failing instantly and entirely on brief network blips or timeouts, leading to cascaded application failures without graceful degradation.
**Why it existed:** Quick-to-market development neglected proper transient error handling and connection pool protection, treating remote service boundaries like local calls.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retries` (Exponential Backoff) and `@circuit_breaker` decorators. Wrapped all critical external dependencies in these robust decorators. Added a `/health` endpoint to actively monitor service vitality.
**Blast radius before:** Any intermittent DNS failure or 503 response from Groq, Twilio, or local services would immediately surface as a 500 error to the end-user, halting authentication or security scanning processes.
**Watch for:** Other background sync jobs or webhook integrations that might still assume a perfectly reliable network. Future integrations must use these resilience decorators.
