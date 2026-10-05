## 2024-05-17 — External Dependency Resilience
**Failure point found:** External API calls (Honeypot.is, Twilio, SendGrid, Groq) were missing retry logic and circuit breakers. Failures in OTP sending were swallowed and presented as success to the user.
**Why it existed:** Happy-path driven development during initial integration.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retry_sync`, `@with_retry_async`, and `CircuitBreaker`. Wrapped `utils/crypto.py`, `api/auth.py`, and `api/detection.py` with these safeguards. OTP endpoints now fail explicitly when down, rather than misleading the user. Detection degrades gracefully.
**Blast radius before:** Silent failure of critical authentication pathways (users stranded), thread exhaustion from hanging third-party API calls without timeouts.
**Watch for:** Other outbound HTTP requests in `backend/services/` that still rely on raw `requests.get()` without timeouts or circuit breakers (e.g., `ollama_scan.py`, `openclaw_agent.py`).
