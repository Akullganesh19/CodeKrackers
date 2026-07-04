## 2024-05-18 — External AI & Notification Resilience

**Failure point found:** Twilio SMS notification (`send_threat_alert`) and AI Scans (`ai_deep_scan`, `ollama_deep_scan`) lacked any automated recovery mechanisms (retries, backoff, or circuit breaking). An external outage (e.g., Twilio timeout or Groq down) would either repeatedly hang/fail threads or silently swallow errors without tripping a degraded mode.

**Why it existed:** Quick implementation of external services focusing on happy-path SMS generation and AI scanning without anticipating transient network issues or API rate limits. Exceptions in `send_threat_alert` were swallowed and returned `False`, masking the issue from potential circuit breakers.

**Recovery built:**
1. Added `@circuit_breaker(failure_threshold=3, recovery_timeout=30.0)` and `@with_retries(max_attempts=3, initial_backoff=0.5, backoff_factor=2.0)` to `send_threat_alert`.
2. Added `@circuit_breaker(failure_threshold=3, recovery_timeout=60.0)` and `@with_retries(max_attempts=3, initial_backoff=1.0, backoff_factor=2.0)` to `ai_deep_scan`.
3. Added `@circuit_breaker(failure_threshold=2, recovery_timeout=60.0)` and `@with_retries(max_attempts=2, initial_backoff=0.5, backoff_factor=1.5)` to `ollama_deep_scan`.
4. Removed swallowed exceptions in these service functions, properly bubbling them up to correctly trigger retries and open the circuit breaker when necessary.
5. Added `try/except` fallbacks in the callers (`spam_shield.py` and `ai_deep_scan.py` for Ollama fallback) to log gracefully and ensure the primary business logic (spam processing) completes successfully even if the notification or AI scan circuits are open.

**Blast radius before:** High. If Twilio experienced a transient error during a critical high-threat SMS block, the user would not be notified, but the threat would be blocked. However, repeated attempts on a down API could tie up backend threads. For AI scans, a down Groq API could cause delays in processing every incoming SMS.

**Watch for:** Ensure other external API integrations (e.g., SendGrid, custom external webhooks) are wrapped similarly and do not swallow exceptions internally.
