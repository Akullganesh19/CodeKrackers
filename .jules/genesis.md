## 2024-07-08 — Outbound Integration Resilience

**Failure point found:** Unprotected synchronous calls to external services (Twilio, SendGrid, Groq API, and local Ollama) in `auth.py`, `notifier.py`, `ai_deep_scan.py` and `ollama_scan.py`. These lacked retry logic on transient failure, leaving the system fragile to momentary network blips or external service rate limits.
**Why it existed:** The code directly invoked the clients (`client.messages.create`, `requests.post`, `client.chat.completions.create`) within primary operational flows without any abstraction for robustness.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retries` (exponential backoff) and `@circuit_breaker` (fails fast on systemic outage) decorators for both sync and async operations. Applied them to all outbound network calls and wrapped them in graceful fallback/catch handlers.
**Blast radius before:** Any network hiccup with Twilio/SendGrid would fail the OTP send, preventing a user from logging in or failing to send threat alerts. A timeout connecting to Groq or Ollama would completely fail the threat scan.
**Watch for:** Other un-wrapped network calls (such as fetching data from remote webhooks) that might slip in without going through `backend/core/resilience.py` wrappers.
