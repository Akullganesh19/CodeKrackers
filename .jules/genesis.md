## 2024-05-18 — [Resilience for Outbound Integrations]
**Failure point found:** External API calls to Groq (AI Scan) and Twilio (SMS Notifier) had no retry mechanisms, circuit breakers, or backoff logic.
**Why it existed:** Quick implementation prioritized functionality over stability in external integrations.
**Recovery built:** Added `@circuit_breaker` and `@with_retries` decorators in `backend/core/resilience.py`. Applied these to `_call_groq` in `ai_deep_scan.py` and `_send_twilio_message` in `notifier.py`.
**Blast radius before:** A transient failure in Groq or Twilio would immediately fail the entire request, disrupting SMS delivery and AI analysis across all users.
**Watch for:** Other third-party integrations (e.g., Sendgrid, Redis) that might lack retry or circuit-breaking logic.
