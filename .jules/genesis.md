## 2024-06-25 — External Dependencies Fallback

**Failure point found:**
Unprotected External Calls (HTTP requests without retry on transient failure and no Circuit Breakers). Services calling Groq Cloud, Twilio (Notifications & OTP), OpenClaw Gateway, and local Ollama would fail loudly on a single failure, immediately raising exceptions, or simply hanging requests if network connectivity dropped.

**Why it existed:**
Initial implementations of `ai_deep_scan`, `notifier` and `openclaw_agent` assumed perfect connectivity and instant responses from third-party and local microservices APIs.

**Recovery built:**
1. Added exponential backoff (`@with_retry_sync`) and `@CircuitBreaker` decorators in `backend/core/resilience.py`.
2. Extracted pure HTTP external calls in services into `_call_*` helper methods and decorated them with `@CircuitBreaker(failure_threshold=3)` as the outermost layer and `@with_retry_sync(max_attempts=3, initial_backoff=0.5)`.
3. Re-wired original functions to execute these helpers inside `try-except` blocks, returning predefined fallback signatures (e.g. `{"score_increase": 0.0, "reason": "..."}`) when the circuit breaker blows or retries are exhausted.
4. Added a `GET /api/health` check endpoint.

**Blast radius before:**
Any minor hiccup with Groq or Twilio resulted in exceptions disrupting the user's flow and causing potential unhandled errors upstream. Single points of failure existed.

**Watch for:**
Other background jobs calling databases or external webhooks without idempotency protection or retry logic. Check `backend/services/evidence_chain.py` or database writes where connections can fail.
