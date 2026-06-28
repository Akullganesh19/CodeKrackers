## 2024-05-19 — Added Central Resilience Layer
**Failure point found:** External API calls (Groq, Ollama, Twilio, Sendgrid, Honeypot.is) were unprotected from transient failures, rate limits, and prolonged outages.
**Why it existed:** System was built assuming happy paths and 100% uptime for these external services.
**Recovery built:** Created `backend/core/resilience.py` featuring `@with_retries` (exponential backoff) and `@circuit_breaker` decorators. Applied these to auth SMS/Email OTP sends, AI scans (Groq, Ollama), and crypto address lookups.
**Blast radius before:** Transient 500s from Twilio would break OTP login. Groq downtime would block threat scanning.
**Watch for:** Other integrations directly utilizing `requests` or `httpx` without protective decorators.
