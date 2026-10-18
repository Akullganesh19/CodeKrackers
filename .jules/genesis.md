## 2024-10-18 — AI Service Fallbacks and Retries

**Failure point found:** AI analysis services (`ollama_scan.py`, `ai_deep_scan.py`, `openclaw_agent.py`) were making direct HTTP requests and API calls without retry mechanisms or circuit breakers. A transient failure (like a timeout) or a service outage (Ollama down, Groq API limits) would immediately fail the entire request, leading to missing threat assessments.

**Why it existed:** Initial implementation focused on core logic, assuming high availability of the underlying AI models.

**Recovery built:**
1. Added a resilience module (`backend/core/resilience.py`) with `@with_retry_sync`, `@with_retry_async`, and a `@CircuitBreaker` class.
2. Wrapped HTTP and Groq SDK calls in these decorators.
3. Implemented a fallback mechanism in the CircuitBreaker so that if a service trips, it gracefully returns a neutral risk score instead of blocking processing or crashing the application.

**Blast radius before:** High. If Ollama or Groq was unavailable, all incoming messages or voice transcripts would fail their AI threat scan, leaving users unprotected against sophisticated, AI-detectable scams.

**Watch for:** Other integrations, such as the `CYBERCRIME_PORTAL_URL` webhook or external databases, which may also lack these robust resilience patterns.
