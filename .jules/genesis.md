## YYYY-MM-DD — Protect External API Integrations (Twilio, Groq, Ollama)
**Failure point found:**
1. `backend/services/ai_deep_scan.py` calls Groq LLM API and `requests.get("http://localhost:11434")` (Ollama) without any retry on transient failures. It just returns an error silently or falls back immediately on transient network failures.
2. `backend/services/ollama_scan.py` calls Ollama via `requests.post()` without any retry for transient failures, returning immediately.
3. `backend/services/openclaw_agent.py` calls `requests.get()` without any retries.
4. `backend/services/notifier.py` calls Twilio via `twilio.rest.Client` for both `send_threat_alert` and `send_otp`, and if it fails, it just logs an error and returns `False` or a simulated OTP, with NO retries for transient HTTP errors from Twilio's API.
5. In `backend/api/auth.py`, Twilio and Sendgrid are called directly with `try/except`, but no retry is attempted. A single timeout drops the OTP.

**Why it existed:** Developers likely assumed these APIs have 100% uptime and didn't anticipate transient network glitches or rate-limit timeouts.
**Recovery built:**
- Added a centralized `resilience.py` module providing `@with_retry_sync` and `@CircuitBreaker` decorators.
- Wrapped Groq and Ollama API calls with `with_retry_sync` (and a CircuitBreaker for Groq to fail fast if Groq goes down).
- Wrapped Twilio and Sendgrid API calls with `with_retry_sync`.
**Blast radius before:** High. A single network blip or a rate limit would cause AI deep scans to fail silently to 0%, or worse, cause OTPs to fail to send (locking out users completely).
**Watch for:** Other direct `requests.post` or `requests.get` calls in newly added services.
