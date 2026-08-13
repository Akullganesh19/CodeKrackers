## $(date +%Y-%m-%d) — Self-Healing Resilience Primitives for External Dependencies

**Failure point found:**
1. Unprotected requests to external LLM providers (Ollama, Groq) with no retry or fallback mechanisms.
2. Unprotected requests to OpenClaw Autonomous Agent Gateway with no failure limits or retries.
3. Completely missing `backend/core/resilience.py` module in the codebase despite memories referencing its tools (`@with_retry_sync`, `@with_retry`, `CircuitBreaker`).

**Why it existed:**
Developers likely assumed APIs were 100% reliable, leaving transient network errors or temporary service downtimes to fatally crash internal processes and block users without warning or recovery paths.

**Recovery built:**
1. **Core Utilities (`backend/core/resilience.py`)**: Built `CircuitBreaker`, `@with_retry_sync`, and `@with_retry` tools from scratch. Implemented thread-safe locks on Circuit Breaker state management.
2. **AI Deep Scan (`ai_deep_scan.py`)**: Added a Circuit Breaker (5 failures / 5 min timeout) and `@with_retry_sync` to the Groq fallback execution to gracefully handle cloud API rate limits or transient connection drops.
3. **Local AI Scan (`ollama_scan.py`)**: Wrapped the native HTTP requests to Ollama with an exponential backoff retry mechanism to survive short local server hiccups.
4. **OpenClaw Agent (`openclaw_agent.py`)**: Wrapped the health check calls in a fast-failing Circuit Breaker (3 failures / 1 min timeout) and an exponential backoff retry to prevent hanging the system when the local gateway goes down.

**Blast radius before:**
Any brief external network failure or AI API rate limit would immediately throw an exception, potentially crashing background tasks or returning 500s directly to users for core threat detection features.

**Watch for:**
We must check for other database/Redis failure points (e.g. `redis_client` instantiation) or webhook deliveries (like Twilio / Sendgrid in `notifier.py`) that might need similar circuit breaker or retry configurations.
