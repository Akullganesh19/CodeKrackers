## 2025-05-15 — Outbound API Resilience

**Failure point found:**
Synchronous outbound HTTP calls to Twilio, SendGrid, and Groq APIs were being made across multiple services (`notifier.py`, `auth.py`, `ai_deep_scan.py`, `ollama_scan.py`). These calls lacked retry mechanisms for transient network issues or rate limits, and they had no circuit breakers.

**Why it existed:**
Initial implementations favored simplicity, wrapping the API calls in a basic `try/except` to log errors, but fundamentally failing the operation on the first transient error.

**Recovery built:**
1. Created `backend/core/resilience.py` introducing `@circuit_breaker` and `@with_retries` decorators for both sync and async functions. The retry mechanism uses exponential backoff.
2. Extracted inline outbound calls in `ai_deep_scan.py` (Groq API) and `auth.py` (Twilio/SendGrid APIs) into isolated functions.
3. Applied the resilience decorators to these isolated functions, as well as `send_threat_alert` and `send_otp` in `notifier.py`, and `ollama_deep_scan` in `ollama_scan.py`.
4. Ensure callers catch exceptions (like `CircuitBreakerOpenException`) to allow graceful degradation (e.g., in `spam_shield.py`, logging the error and moving on instead of crashing the spam check).

**Blast radius before:**
If an external service went down or a transient network glitch occurred, users wouldn't receive OTPs (locking them out), AI scans would silently fail and miss threats, and threat alerts wouldn't be sent, all while putting unneeded load on our downstream dependencies.

**Watch for:**
Other components making direct outbound calls (e.g. database connections or other integrations) without using the `resilience` module decorators.
