## 2024-08-12 — Auto-Retry and Circuit Breakers for External APIs
**Failure point found:**
1. Authentication (`backend/api/auth.py`) silently swallowed Twilio and SendGrid OTP sending failures, returning success to the user when the gateways failed, causing users to wait for OTPs that would never arrive.
2. AI Deep Scan (`backend/services/ai_deep_scan.py`) called the Groq Cloud API synchronously with no retries or timeout protection, meaning transient API failures caused analysis to crash instantly, and prolonged outages could cascade to block scan requests.

**Why it existed:** The implementations favored happy-path development for quick API integration without considering transient network faults, third-party downtime, or rate limiting.

**Recovery built:**
1. Created `backend/core/resilience.py` with exponential backoff retry decorators (`@with_retry`, `@with_retry_sync`) and a thread-safe `CircuitBreaker`.
2. Extracted OTP sending logic and wrapped them in retries. Hard failures now throw HTTP 503 instead of masking the error.
3. Extracted the Groq API call, wrapped it in a 3-attempt exponential backoff retry, and protected it behind a Circuit Breaker that fails fast and degrades gracefully when the upstream is down.

**Blast radius before:**
Any Twilio/SendGrid hiccup resulted in users permanently stuck on the login screen. Any Groq API hiccup resulted in skipped threat analysis or delayed processing across the board.

**Watch for:** Other external dependencies missing retries, such as direct webhook calls, `requests.post()` calls without timeouts, or database queries prone to transient connection drops.
