## 2025-02-26 — AI & Agent Service Resilience
**Failure point found:** External calls in `backend/services/ollama_scan.py`, `backend/services/ai_deep_scan.py`, and `backend/services/openclaw_agent.py` were using bare `requests` or `Groq` clients with no retry logic on transient failure and no circuit breakers.
**Why it existed:** The original implementation assumed these external AI services and local agents would always be available and respond instantly without transient network errors.
**Recovery built:** Implemented a robust `CircuitBreaker` and exponential backoff retry mechanism (`@with_retry_sync`) in `backend/core/resilience.py`. These decorators were applied to all external HTTP/API calls across the three services.
**Blast radius before:** Any transient network blip or temporary service outage (e.g., rate limiting on Groq) would cause the entire analysis to fail immediately, leading to degraded threat intelligence scoring. A persistent outage could cause cascading latency issues.
**Watch for:** Other third-party integrations (like SMS gateways or webhooks) that might also be using bare HTTP requests without resilience wrappers.
