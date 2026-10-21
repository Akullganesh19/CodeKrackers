## 2024-05-18 — AI and Notifier Circuit Breakers
**Failure point found:** `ai_deep_scan`, `send_threat_alert`, and `send_otp` failed silently by swallowing errors, or didn't retry transient failures.
**Why it existed:** Quick scaffolding of external APIs without resilience engineering.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retry_sync` and `@CircuitBreaker`. Wrapped AI and Twilio endpoints.
**Blast radius before:** Users received no notifications if SMS failed once, and threat scanning crashed silently leaving models exposed.
**Watch for:** Other external HTTP requests (e.g., in analytics or other new microservices) that might need `@with_retry_async` or `@CircuitBreaker`.
