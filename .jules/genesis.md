## 2024-05-18 — Add resilience to external AI and SMS/Email APIs
**Failure point found:** External calls to Groq API (`ai_deep_scan`), local Ollama (`ollama_deep_scan`), Twilio (`send_threat_alert`, `send_otp`), and SendGrid (`send_otp`) lacked retry mechanisms or circuit breakers.
**Why it existed:** Historically assumed external services would be 100% reliable, leading to brittle application behavior during transient network blips or third-party outages.
**Recovery built:** Created `@with_retries` and `@circuit_breaker` decorators in `backend/core/resilience.py`. Wrapped `_call_ollama`, `_call_groq`, `_send_twilio_message`, `_send_twilio_auth`, and `_send_sendgrid_auth` inside these decorators to ensure automatic retries and fallback execution when thresholds are reached.
**Blast radius before:** Any transient API failure would cause missed threat alerts, failed AI scanning, or broken authentication loops for users.
**Watch for:** Other third-party integrations (like `check_sms_spam.py` or new gateways) being introduced without decorators.
