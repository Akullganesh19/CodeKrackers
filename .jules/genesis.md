## 2024-11-20 — Genesis Self-Healing Architecture Updates

**Failure point found:** Unprotected external API calls in Twilio notifications and AI Scanners (Groq Cloud and Local Ollama).
**Why it existed:** Historical assumption of network reliability; missing standard retry/resilience layers.
**Recovery built:** Created `backend/core/resilience.py` introducing `@with_retries` (exponential backoff) and `@circuit_breaker`. Applied these to `notifier.py` (Twilio SMS/OTP), `ai_deep_scan.py` (Groq API), and `ollama_scan.py` (Ollama local endpoint).
**Blast radius before:** Any temporary network glitch or rate-limiting would instantly cause missed critical SMS alerts or failed AI threat scans with no automatic recovery.
**Watch for:** Other un-abstracted external network requests (e.g., blockchain API integrations or other webhook endpoints) lacking similar resilience decorators.
