## 2024-05-18 — Circuit Breakers and Retry Logic
**Failure point found:** Unprotected third-party API calls (Groq AI, Twilio SMS, SendGrid). If these went down, they would throw unhandled exceptions and potentially cascade or hang threads.
**Why it existed:** Quick implementation of features without considering external service unreliability.
**Recovery built:** Implemented `CircuitBreaker` pattern and exponential backoff retries (`with_retry_sync`) in `backend/core/resilience.py`. Wrapped Groq, Twilio, and SendGrid calls with these mechanisms.
**Blast radius before:** 100% of affected requests would fail hard, potentially taking down the main API server threads due to hangs.
**Watch for:** Other external HTTP requests (e.g., webhook calls) that might need similar protection.
