## 2026-06-21 — Added Resilience to External APIs (Twilio, Honeypot, Ollama)

**Failure point found:** External service calls (`client.messages.create` for Twilio, `client.get` for Honeypot, `requests.post` for Ollama) were not protected by any retry or circuit breaking logic.
**Why it existed:** The backend assumed happy-path network connectivity and 100% uptime from external APIs, prioritizing rapid development of core logic over resilience.
**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retries`, `@async_with_retries`, `@circuit_breaker`, and `@async_circuit_breaker`.
2. Wrapped Twilio SMS API calls in `backend/services/notifier.py` with retries.
3. Wrapped Crypto Honeypot checking API calls in `backend/utils/crypto.py` with async retries.
4. Wrapped local Ollama scan calls in `backend/services/ollama_scan.py` with both retries and a circuit breaker (trips after 3 failures).
**Blast radius before:**
- Twilio failures: Silent dropping of OTPs and alert notifications (Critical severity).
- Honeypot/Ollama failures: Immediate failure of threat detection workflows, returning unhandled exceptions or skipping AI logic entirely for the duration of the timeout.
**Watch for:** Other external API calls in the app (e.g. `requests.get`, `httpx.AsyncClient`) that may still be missing retry logic and circuit breakers.
