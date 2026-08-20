## 2024-08-20 — Self-Healing HTTP Clients

**Failure point found:** Multiple AI and forensic services (`ollama_scan.py`, `ai_deep_scan.py`, `openclaw_agent.py`) made unprotected HTTP calls to external/local services (Ollama, OpenClaw, Groq) using raw `requests.get/post` or `client.chat.completions.create` without retries, exponential backoff, or circuit breakers.

**Why it existed:** Quick integration during the hackathon/prototyping phase favored happy-path development over defensive programming.

**Recovery built:**
1. Created `backend/core/resilience.py` with `@with_retry_sync`, `@with_retry`, and a thread-safe `@CircuitBreaker`.
2. Extracted HTTP calls into dedicated helper functions (`_do_ollama_request`, `_check_openclaw_gateway`, `_check_ollama_gateway`, `_do_groq_request`) and decorated them with retries and circuit breakers.
3. Used `response.raise_for_status()` inside helpers to ensure HTTP errors correctly trigger the retry/backoff mechanisms.

**Blast radius before:** A momentary network blip or a slow Ollama/Groq model response would cause the entire scan to fail instantly. Repeated failures would continue to hammer a struggling service, risking cascading failure.

**Watch for:** Other integrations calling external APIs (e.g., Twilio in `notifier.py`) that might need similar resilience primitives, or database operations that could suffer from transient connection loss.
