## 2024-05-18 — AI & Notification Self-Healing Architecture
**Failure point found:** External service calls (Ollama, Groq API, Twilio, OpenClaw Agent) had no retry logic or circuit breakers. A transient network failure or service hiccup would immediately fail the operation or swallow errors silently, potentially missing threat alerts or failing authentication.
**Why it existed:** MVP implementation assumed happy paths and reliable network connections. Error handling was limited to logging and returning default values.
**Recovery built:**
1. Added a `resilience.py` core module with exponential backoff retries (`@with_retry_sync`, `@with_retry_async`) and a `CircuitBreaker`.
2. Applied `@with_retry_sync` and `@CircuitBreaker` to `ollama_deep_scan` to prevent hammering a down local service.
3. Applied `@with_retry_sync` to `send_threat_alert` and `send_otp` in `notifier.py` to ensure critical alerts and MFA codes reach users.
4. Applied `@with_retry_sync` to the internal Groq API call inside `ai_deep_scan`.
5. Applied `@with_retry_sync` to `openclaw_analysis`.
**Blast radius before:** Any temporary API downtime or network blip caused silent failure of threat scanning or missed critical notifications.
**Watch for:** Other database or external API calls (e.g. phone intel, other integrations) that might still lack backoff/retry strategies.
