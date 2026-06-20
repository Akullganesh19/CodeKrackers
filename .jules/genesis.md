## 2025-06-20 — Genesis: Self-Healing Architecture Additions

**Failure point found:** External API calls (Groq Cloud API, Twilio SMS) and local service dependencies (Ollama) lacked retry mechanisms, and the app lacked a degraded/fallback mode when the Groq Cloud API timed out or failed. This created a single point of failure where transient network errors or third-party outages would crash requests or hang the application indefinitely.
**Why it existed:** The application was built with a "happy path" first approach, assuming external services are always reliable and fast.
**Recovery built:**
1. Implemented generic `with_retries` and `circuit_breaker` decorators in a new `backend/core/resilience.py` module to add exponential backoff and circuit-breaking capabilities.
2. Wrapped the Groq Cloud API call in `backend/services/ai_deep_scan.py` with `with_retries` and `circuit_breaker`, and implemented a safe fallback default score when the circuit is open. Added a 10s timeout to the Groq API call.
3. Wrapped Twilio SMS operations (threat alerts and OTP) in `backend/services/notifier.py` with `with_retries`.
4. Wrapped the local Ollama request in `backend/services/ollama_scan.py` with `with_retries`.
5. Created a `/health` endpoint in `backend/main.py` for monitoring database and Ollama availability.
**Blast radius before:** Any temporary Groq, Twilio, or Ollama failure would result in immediate 500 errors to the user or silent failure of critical threat alerts/OTP sending. Slow responses from Groq could tie up workers.
**Watch for:** Ensure new external API integrations use these resilience decorators.
