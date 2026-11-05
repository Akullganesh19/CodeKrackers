## 2024-05-24 — Add Resilience Core
**Failure point found:** External calls (Twilio, SendGrid, Groq, Ollama) in notifier, auth and AI scan services lacked retry and circuit breaker logic, failing silently or hanging.
**Why it existed:** Initially built as happy-path prototypes without transient failure handling.
**Recovery built:** Created `backend/core/resilience.py` with `@CircuitBreaker`, `@with_retry_sync`, and `@with_retry_async`. Applied them to `notifier.py`, `auth.py`, `ai_deep_scan.py`, and `ollama_scan.py`.
**Blast radius before:** Any transient API error would fail notifications or threat scans completely.
**Watch for:** Other outbound API calls missing these decorators.
