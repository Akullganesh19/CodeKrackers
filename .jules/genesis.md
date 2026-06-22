## 2024-05-18 — [Resilience Module Added]
**Failure point found:** External calls to `requests.get`, `requests.post`, and `Twilio Client` in services like `ai_deep_scan`, `ollama_scan`, `openclaw_agent`, and `notifier` are unprotected and will crash or hang indefinitely if the dependency is down or slow.
**Why it existed:** Quick implementation without anticipating transient network failures or service outages.
**Recovery built:** Created `backend/core/resilience.py` containing `@with_retries`, `@async_with_retries`, `CircuitBreaker`, `@circuit_breaker`, and `@async_circuit_breaker`. Integrated these into high-risk external API calls.
**Blast radius before:** A single timeout or 500 error from a local Ollama instance or external API would bring down the entire endpoint or background task without retry.
**Watch for:** Ensure we do not add retries to non-idempotent operations without an idempotency key.
