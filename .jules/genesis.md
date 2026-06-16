## 2024-05-18 — AI & External API Fallback Resilience
**Failure point found:** External API calls (Groq AI, Ollama, and Honeypot.is) lacked transient error handling. Network blips or 5xx responses were swallowed silently, resulting in a safe default (e.g., returning 0.0 threat score for AI scans).
**Why it existed:** Happy-path development without defensive layers against external service degradation.
**Recovery built:** Created `@with_retries` and `@async_with_retries` decorators in `backend/core/resilience.py`. Extracted vulnerable API calls and applied these decorators with exponential backoff.
**Blast radius before:** Any temporary API timeout or error would cause the app to fail-open, marking potential scams as safe without alerting the user.
**Watch for:** Other external HTTP requests in new services that don't utilize `resilience.py`.
