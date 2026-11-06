## 2025-02-12 — Twilio API & Groq API Unprotected Failures
**Failure point found:** `send_threat_alert` and `send_otp` in `notifier.py` called the Twilio API without any circuit breaking. Also, the Groq API call in `ai_deep_scan.py` lacked circuit breaking.
**Why it existed:** Initially written assuming these external services are always available, leading to potential cascading failures if Twilio or Groq outages occur.
**Recovery built:** Implemented `CircuitBreaker` pattern in `backend/core/resilience.py`. Added circuit breakers to Twilio SMS endpoints (`@twilio_cb` in `notifier.py`) and Groq AI calls (`@groq_cb` in `ai_deep_scan.py` with fallback returning an empty score).
**Blast radius before:** Twilio/Groq API failures could hang or fail requests rapidly, potentially propagating 500s across auth or scanning endpoints if repeated too quickly.
**Watch for:** Other third-party integrations (e.g., SendGrid) missing circuit breakers.
