## 2024-06-23 — [Added Automatic Resiliency for External AI & SMS Dependencies]

**Failure point found:** External network dependencies (Twilio SMS, Local Ollama AI, Groq Cloud AI) were unprotected. Transient 5xx errors, rate limits, or a crashed local AI instance caused silent dropped notifications or unhandled hanging application threads.
**Why it existed:** Historical reasons: Proof-of-concept integrations often prioritize happy-path API consumption without addressing real-world network turbulence and cloud/on-device failure states.
**Recovery built:** Created `backend/core/resilience.py` with reusable `@with_retries` (exponential backoff) and `@circuit_breaker` decorators. Applied to Twilio OTP/alert SMS delivery, Ollama local AI scanning, and Groq cloud fallback scanning.
**Blast radius before:**
- Twilio drops meant users couldn't receive critical OTPs or fraud alerts if Twilio dropped a request.
- Ollama crash meant every Deep Scan would hang the request timeout limit (30 seconds) and potentially lock up threads.
- Groq cloud rate limiting meant a failure to fallback.
**Watch for:** Other external dependencies that perform I/O over HTTP, particularly the OpenClaw Gateway or future DB external hooks, that may also lack retry/circuit-breaking protections.