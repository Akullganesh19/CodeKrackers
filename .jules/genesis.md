## $(date +%Y-%m-%d) — Unprotected external network calls

**Failure point found:** External network calls (Twilio SMS, Groq Cloud API, Ollama Local API, Nitro Enclave Vsock) had no retry, fallback, or circuit breaker mechanisms.
**Why it existed:** Initially built with happy-path logic, assuming external APIs and local services are always highly available.
**Recovery built:** Created a robust `CircuitBreaker` pattern in `backend/core/resilience.py` with both exponential backoff retries (`@with_retry_sync`) and explicit failover fallbacks to prevent cascading failures.
**Blast radius before:** Any transient API error or service degradation would cause unhandled exceptions, potentially taking down parent API routes (e.g. blocking threat alerts or child lock SMS verifications) or slowing down the whole system if timeouts lingered.
**Watch for:** Other areas where external SDKs or direct socket connections might lack timeout or retry logic, such as raw `requests.post()` calls scattered in undocumented analytics layers.
