## 2024-06-25 — Added Circuit Breakers for AI Services
**Failure point found:** External calls to AI services (Groq, Ollama, OpenClaw) had no retry mechanisms, circuit breakers, or robust fallbacks.
**Why it existed:** Quick integrations for MVP.
**Recovery built:** Implemented a CircuitBreaker decorator in `backend/core/resilience.py` and applied it to AI service calls. If services fail multiple times, they fallback immediately to a default response.
**Blast radius before:** Repeated slow timeouts and unhandled exceptions when AI models were down, taking down parts of the threat analysis flow.
**Watch for:** Ensure we don't spam failed services, test edge cases in circuit breaker logic.
## 2024-06-25 — Added Circuit Breakers for External Network Calls (Twilio SMS)
**Failure point found:** Twilio SMS notifications (`send_threat_alert`, `send_otp`) had no Circuit Breaker, leading to continuous slow timeouts if Twilio was down.
**Why it existed:** MVP implementation relying on simple try/catch without backoff or circuit breaking.
**Recovery built:** Wrapped Twilio external network calls with `@CircuitBreaker(failure_threshold=3, recovery_timeout_secs=30)` using fallback mechanisms that simulate sending in logs (for OTP) and gracefully handle failures (for alerts).
**Blast radius before:** Users attempting login or triggering alerts when Twilio was down would experience massive delays as requests hung until standard HTTP timeouts.
**Watch for:** Ensure we don't inadvertently mock production OTPs for legitimate traffic if Twilio trips, which could cause authentication issues.
