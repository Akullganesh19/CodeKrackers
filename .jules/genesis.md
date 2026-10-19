## 2024-05-18 — External Service Resilience
**Failure point found:** External API calls to Groq (`ai_deep_scan`), Ollama (`ollama_scan`), OpenClaw (`openclaw_agent`), and Twilio (`notifier`) had no backoff and failed instantly. They swallowed exceptions and returned defaults or False, hiding potential transient errors.
**Why it existed:** Simplicity during MVP. Immediate failing was easier than implementing robust retry logic.
**Recovery built:** Created `CircuitBreaker` and `with_retry_sync` decorators in `backend/core/resilience.py`. Applied them to all four external services. Re-raised exceptions so circuit breaker could detect failures, with proper fallback returns when circuit is OPEN.
**Blast radius before:** Any transient network issue to Twilio prevented threat alerts or OTPs. A momentary hiccup in Groq or Ollama caused the AI deep scan to fail and fall back to zero without trying again. OpenClaw failure was immediate.
**Watch for:** Other outbound HTTP calls (e.g., `requests` in new services) or database operations that might benefit from async retries.
