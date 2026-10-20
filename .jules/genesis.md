## 2025-01-20 — External Dependency Resilience
**Failure point found:** Multiple external dependencies (Twilio SMS, Groq Cloud API, Ollama Local API, OpenClaw Agent) were invoked without retry policies, timeouts, or circuit breakers. Failures would either hang, crash the request context, or be swallowed silently with no graceful fallback.
**Why it existed:** MVP phase implementation focused on happy-path functionality. External HTTP calls were assumed to be 100% reliable.
**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retry_sync`, `@with_retry_async`, and `CircuitBreaker`.
2. Applied `@CircuitBreaker` and `@with_retry_sync` to `send_threat_alert` and `send_otp` in `notifier.py` with simulation fallbacks.
3. Applied to `ollama_deep_scan` in `ollama_scan.py` with fallback to default zero-risk dictionary.
4. Extracted `call_groq` in `ai_deep_scan.py` and applied resilience decorators with zero-risk fallback.
5. Applied to `openclaw_analysis` in `openclaw_agent.py` to prevent hanging requests when the autonomous agent is down.
**Blast radius before:** Any transient network issue to Groq or Twilio would fail the user request completely (e.g., failing to deliver OTPs, blocking login).
**Watch for:** Ensure we do not swallow exceptions inside the wrapped functions, as this prevents the Circuit Breaker and retry logic from firing.
