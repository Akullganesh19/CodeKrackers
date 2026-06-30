## 2024-05-24 — Self-Healing External Dependencies

**Failure point found:** External API integrations (Twilio, Groq, local Ollama) lacked recovery handling. Any transient network failure or upstream 500 resulted in immediate, unprotected exceptions, failing core operations like OTP delivery, threat alerts, and deep scanning.
**Why it existed:** Quick initial integration prioritized happy path implementation over production resilience and graceful degradation.
**Recovery built:** Implemented `with_retries` (exponential backoff) and `circuit_breaker` decorators in `backend/core/resilience.py`. Applied these to `_twilio_send_message`, `_call_ollama`, and `_call_groq`. If Ollama's circuit opens, `ai_deep_scan` automatically degrades to the Groq fallback. If Groq also fails, it degrades gracefully to returning a 0 score without crashing.
**Blast radius before:** Any Twilio hiccup prevented logins (OTP). Any Groq/Ollama hiccup failed the entire SMS/Voice analysis pipeline.
**Watch for:** Other integrations like SendGrid or Cybecrime Portal webhooks that might lack retry and circuit breaking mechanisms.
