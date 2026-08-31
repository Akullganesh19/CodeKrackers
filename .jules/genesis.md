## 2024-05-18 — [Resilient AI Scanning]
**Failure point found:** External calls to both Groq API (`ai_deep_scan.py`) and local Ollama (`ollama_scan.py`) were unprotected against transient network failures and rate limits.
**Why it existed:** The initial implementation prioritized functionality over robustness, assuming the AI endpoints would always be available and respond quickly.
**Recovery built:** Added `@CircuitBreaker` and `@with_retry_sync` decorators to isolate the HTTP/API calls into global helper functions. This ensures retries with exponential backoff for transient issues and fails fast using a circuit breaker if the service goes down completely.
**Blast radius before:** Any temporary API blip or rate limit would cause the threat analysis to silently fail and fall back to 0.0 score, potentially allowing scams through.
**Watch for:** Other third-party integrations (like Twilio in `notifier.py` or OpenClaw gateway calls) that might lack similar resilience wrappers.
