## 2024-05-19 — Added Resilience Mechanisms to External APIs

**Failure point found:**
External API calls (`check_crypto_honeypot` using honeypot.is API and `ollama_deep_scan` using a local Ollama instance) were completely unprotected. A failure or timeout in these services would either crash the calling code or immediately fail the operation with a fallback, causing a brittle system state without attempting to recover.

**Why it existed:**
The application was written with a "happy path" first mindset, assuming that external dependencies will always be up, or returning basic fallback dictionaries without proper retry/backoff strategies to recover from transient faults.

**Recovery built:**
1. Implemented a generalized resilience module (`backend/core/resilience.py`) exposing two key decorators: `@with_retries` (exponential backoff) and `@circuit_breaker`. They natively support both synchronous and asynchronous routines.
2. Wrapped the `check_crypto_honeypot` and `ollama_deep_scan` functions with these decorators, allowing them to automatically retry transient errors and eventually fail fast (open circuit) if the service remains down.
3. Updated the callers (like `backend/api/detection.py`) to catch exceptions raised from the decorators to gracefully fallback, ensuring the user experience degrades gracefully without crashing the app.

**Blast radius before:**
Any transient network blip or a slow local Ollama response would immediately cause threat detection analysis to degrade or throw an exception, potentially halting the detection process for an entire SMS or voice session.

**Watch for:**
Other unprotected external calls such as the ones to `Groq` API inside `ai_deep_scan` and `detect_sms`. Although they have try-catch blocks for fallbacks, they do not currently retry transient network faults. Applying the resilience decorators there could further improve reliability.
