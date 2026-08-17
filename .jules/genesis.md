## 2024-08-17 — Circuit Breakers and Retries for External APIs
**Failure point found:** External HTTP calls to Ollama (AI Deep Scan) and Honeypot.is (Crypto Threat Check) lacked proper retry mechanisms and circuit breakers, potentially blocking threads or leading to silent/cascading failures when downstream services went offline.
**Why it existed:** Quick prototypes typically use raw `requests.post()` and `httpx.get()` calls without considering transient network issues or full downstream outages.
**Recovery built:** Created `backend/core/resilience.py` with `with_retry`, `with_retry_sync`, and thread-safe `CircuitBreaker`. Wrapped `ollama_scan.py` and `crypto.py` APIs in these decorators.
**Blast radius before:** High risk of API gateway hangs or returning unhandled exceptions straight to the UI if a backend model server crashed or honeypot API rate limited us.
**Watch for:** Other unprotected `requests.get()` calls in services like `ai_deep_scan.py` (which still does a raw ping) and `openclaw_agent.py`.
