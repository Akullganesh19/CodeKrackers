## 2025-06-18 — [Resilience for External AI and Notification Dependencies]

**Failure point found:**
Unprotected external calls in critical paths. Specifically, local AI (Ollama) requests, cloud AI (Groq API) requests, Twilio SMS notifications, and OpenClaw agent status checks were executing directly without retry mechanisms or failure limits. A timeout or transient error in these services would cause the requests to immediately fail, potentially skipping important deep scans, dropping critical user alerts, or causing long hangs.

**Why it existed:**
Initial implementations favored simplistic `try/except` blocks without considering network flakiness, rate limits, or complete dependency outages, prioritizing happy-path delivery.

**Recovery built:**
A centralized `backend/core/resilience.py` module was created containing `@with_retries` (exponential backoff) and `@circuit_breaker` (fail-fast to prevent cascading system locks). These decorators were applied to:
1. `backend/services/ollama_scan.py` (Local AI)
2. `backend/services/ai_deep_scan.py` (Cloud AI fallback)
3. `backend/services/notifier.py` (Twilio SMS delivery)
4. `backend/services/openclaw_agent.py` (Agent gateway status)

**Blast radius before:**
Any transient network drop or temporary third-party API issue resulted in silent service degradation, skipped threat detections, or dropped OTP/Alert messages, directly impacting the end user immediately. Repeated timeouts could exhaust system resources (cascading failure).

**Watch for:**
Similar direct `requests.get/post` usage across other backend tasks or new integrations without resilience wrappers. Watch for long-running database queries lacking timeouts or background tasks failing without DLQs.
