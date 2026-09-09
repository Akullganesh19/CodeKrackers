## 2024-05-18 — [Resilience Decorators Added]
**Failure point found:** Fragile external and internal network requests without retries, and unbounded retries blocking services without circuit breaking logic. Unprotected third-party dependencies (Twilio, Groq, Ollama, OpenClaw).
**Why it existed:** Initially built as a quick proof-of-concept hackathon sprint with no proper resiliency or retry mechanisms on API endpoints.
**Recovery built:** Created `@with_retry_sync` and `@CircuitBreaker` resilience decorators in `backend/core/resilience.py`. Applied these to `ai_deep_scan`, `ollama_scan`, and `openclaw_analysis`. Added a `/api/health` endpoint for external monitoring.
**Blast radius before:** High risk of random API integration failures crashing threads or timing out synchronous handlers, resulting in failed scans or dropped text messages with no fallback.
**Watch for:** Other external dependencies that haven't been wrapped in `CircuitBreaker`. Also watch for async functions that need an async version of these decorators.
