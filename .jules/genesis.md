## 2024-05-24 — AI Provider Resilience

**Failure point found:** External calls to Groq API and Ollama API in `backend/services/ai_deep_scan.py` and `backend/services/ollama_scan.py` lacked retry logic, timeout handling, and circuit breakers, meaning a transient failure or provider outage would cascade and crash the scanning functionality.

**Why it existed:** Developers often assume external APIs are always highly available. Initial implementations relied on basic `try/except` without robust recovery strategies like Exponential Backoff, resulting in brittle integrations.

**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retry_sync`, `@with_retry`, and `@CircuitBreaker` decorators.
2. Refactored Groq and Ollama network calls into isolated, decorated functions (`fetch_groq` and `fetch_ollama`).
3. Applied the Circuit Breaker to prevent cascading failures (failing fast when the API is down) and exponential backoff to handle transient 500s or timeouts.

**Blast radius before:** Any network jitter or downtime from Groq or Ollama caused scans to immediately fail and potentially return unhandled exceptions, degrading user experience.

**Watch for:** Other external HTTP requests (e.g., Twilio or SendGrid in `backend/api/auth.py`) that could benefit from similar resilience wrappers.
