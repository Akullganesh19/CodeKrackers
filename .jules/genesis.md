## 2024-07-05 — Add Circuit Breaker and Retry Mechanisms
**Failure point found:** External API calls (Ollama, OpenClaw, Twilio) lack resilience mechanisms like circuit breakers and retries.
**Why it existed:** Initial implementation likely focused on happy path.
**Recovery built:** Added `@circuit_breaker` and `@with_retries` decorators in `backend/core/resilience.py` and applied them to external API calls.
**Blast radius before:** High. Any transient failure or timeout in these external services would cause the calling service to fail, potentially cascading errors or hanging the application.
**Watch for:** Other external dependencies or long-running database queries without timeout/retry handling.
