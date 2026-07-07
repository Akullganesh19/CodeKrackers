## 2024-05-18 — [Automated retries and circuit breakers for external integrations]
**Failure point found:** Outbound API calls (Twilio SMS, Groq AI, Ollama AI) had missing or fragile try/catch handling with zero retry logic. If the network blipped, notifications failed permanently and scans aborted. There was no protection against cascading failure or persistent outages hanging threads.
**Why it existed:** Initially built as happy-path minimum viable code where external APIs were assumed to have 100% uptime.
**Recovery built:** Created `backend/core/resilience.py` containing `@with_retries` (exponential backoff) and `@circuit_breaker` (fails fast after N errors, auto-recovers). Wrapped Twilio, Groq, and Ollama calls with both decorators.
**Blast radius before:** Any transient API error dropped critical user OTPs or disabled the entire AI threat-scanning engine.
**Watch for:** Other outbound integrations (e.g. database connections, OpenClaw agent) that currently lack explicit retry logic or circuit breakers.
