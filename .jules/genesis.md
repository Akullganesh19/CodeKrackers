## 2024-05-24 — Unhandled External API Calls and Blocking Synchronous OTP Providers
**Failure point found:**
1. `ai_deep_scan.py` and `ollama_scan.py` silently caught `Exception` for all external LLM network requests (Groq / Ollama). No retries were configured for transient network errors, and when down, the application would immediately default to 0 scores or fail silently for every request.
2. `auth.py` invoked Twilio and SendGrid synchronous network clients within the main `async def` handler without `await asyncio.to_thread`. This blocked the single-threaded asyncio event loop for all users during execution. Furthermore, failure exceptions were swallowed by `except Exception` blocks, returning HTTP 200 "OTP sent successfully" even when SMS/Email gateways explicitly failed.

**Why it existed:**
Initial implementations of external gateways (LLMs, SMS, Email) focused on rapid integration and "happy path" delivery, utilizing basic `try/except` wrappers for stability without considering backpressure, transient networking failures, or FastAPI event loop concurrency limitations.

**Recovery built:**
1. Created `backend/core/resilience.py` introducing robust `@with_retry_sync`, `@with_retry_async`, and state-based `@CircuitBreaker` utility decorators.
2. Wrapped Groq and Ollama API external calls with synchronous auto-retry configurations (exponential backoff) and a `CircuitBreaker`. This allows transparent degradation (e.g. gracefully returning the fallback and failing fast if the service is truly unavailable), instead of stalling the app and spamming downstream systems.
3. Extracted Twilio and SendGrid OTP sending routines into distinct functions equipped with `@with_retry_sync` and `CircuitBreaker`, wrapped their invocation in `await asyncio.to_thread`, and appropriately raised HTTP 500 when all retries are exhausted to maintain factual REST responses.

**Blast radius before:**
- Network blips to LLMs or Twilio caused immediate service degradation or fake "success" states.
- High latency upstream in Twilio blocked the entire FastAPI worker process (all endpoints for all users were paused until Twilio resolved).
- Users received HTTP 200 "Success" messages while their OTPs failed to deliver, preventing account login entirely.

**Watch for:**
Look for other synchronous requests (e.g., `requests.get` or `requests.post`) lingering inside `async def` FastAPI routes or critical `services/*.py` scripts without retry/circuit breaker decorators.
