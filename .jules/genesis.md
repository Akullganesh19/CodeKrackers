## 2024-05-30 — System-Wide Outbound Call Resilience

**Failure point found:** External third-party integrations (Groq Cloud API, Ollama Local API, OpenClaw Agent Gateway, Twilio SMS API) lacked comprehensive resilience. If these services timed out or returned transient HTTP errors, the application would simply crash, hang, or fail fast without retry logic.
**Why it existed:** Quick proof-of-concept integrations often prioritize happy paths and omit distributed system safeguards like retries, backoff, or circuit breakers.
**Recovery built:** Architected a self-healing resilience layer in `backend/core/resilience.py`.
1. Added `@with_retry_sync` for automated exponential backoff on transient network failures (mitigating blips).
2. Added `@CircuitBreaker` to prevent cascading failures. If a service persistently fails, the circuit opens, immediately routing requests to safe fallback mechanisms without bogging down application threads.
3. Applied these decorators to: `ai_deep_scan` (Groq), `ollama_scan` (Ollama), `openclaw_agent` (OpenClaw), and `notifier` (Twilio).
**Blast radius before:** Any transient API error would propagate to the user, breaking the threat analysis pipeline or failing to deliver critical alerts and OTPs.
**Watch for:** Ensure new external API calls (e.g., database lookup services, third-party threat feeds) are wrapped in these decorators.
