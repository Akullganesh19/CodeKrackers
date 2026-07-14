## 2025-05-19 — Auto-Retry and Circuit Breakers for External API calls
**Failure point found:** External I/O calls to Groq, Twilio, SendGrid, Honeypot.is, and local Ollama lacked robust retry logic or backoff mechanisms, causing hard fails on transient network errors.
**Why it existed:** Quick integrations usually rely on simple try/except blocks without complex failure management or rate limit handling.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retries` (exponential backoff) and `@circuit_breaker` decorators, and applied them to all core third-party dependencies.
**Blast radius before:** Any temporary API downtime or network blip would fail authentication (OTP not sent) or fail deep AI scans, returning 500s or hardcoded fallbacks prematurely.
**Watch for:** Other unsheltered requests using raw `httpx` or `requests` (e.g., webhook processing or new API integrations) that haven't been wrapped in these resilience decorators.
