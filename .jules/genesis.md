## 2024-05-18 — Add Circuit Breaker and Retries for AI Deep Scans
**Failure point found:** External API calls to Groq Cloud and local Ollama services for AI deep threat scanning were unprotected, failing on transient network errors or timeouts.
**Why it existed:** Initial implementation focused on core integration and lacked resilience mechanisms for external dependencies.
**Recovery built:** Wrapped outbound API requests in `@CircuitBreaker` and `@with_retry_sync` decorators to retry transient errors with exponential backoff and trip a circuit breaker if the service stays down.
**Blast radius before:** High. Any network blip or API rate-limit caused deep scans to silently fail and return zero risk scores, allowing sophisticated threats to bypass AI detection.
**Watch for:** Other external integrations (like phone intelligence APIs or OpenClaw agents) that might be making synchronous HTTP calls without retry or circuit breaker patterns.
