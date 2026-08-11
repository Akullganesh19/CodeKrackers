## 2024-05-18 — Auto-Retry with Exponential Backoff for External APIs
**Failure point found:** External API integrations (Groq, Twilio, Ollama) had no transient error recovery. If an API timed out, it failed the entire request or silently dropped important notifications.
**Why it existed:** The original implementations caught the errors and returned fallback values or logged and failed immediately without retrying.
**Recovery built:** Built a central `@with_retry` decorator (`backend/core/resilience.py`) with exponential backoff and applied it to `ai_deep_scan`, `ollama_scan`, and `notifier` (Twilio) services.
**Blast radius before:** Any temporary network blip or 5xx from Groq/Twilio would cause failed scans, missed alerts, and failed user logins (OTP).
**Watch for:** Other third-party integrations (like payment gateways or webhooks) that might lack retry logic. Check if the backoff time blocks requests excessively under high contention.
