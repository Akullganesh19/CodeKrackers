## 2024-05-24 — Added Resilience Primitives (Circuit Breaker & Retry) to External Services
**Failure point found:** Multiple external services (`ollama_scan.py`, `openclaw_agent.py`, `ai_deep_scan.py` for Groq, `crypto.py` for honeypot check) made naive HTTP calls (`requests` and `httpx`) with no retry mechanisms or circuit breaking. If these services failed temporarily or were unavailable, the application would fail fast or return generic failure states without attempting recovery.
**Why it existed:** Quick implementation of API integrations without considering transient network failures or service unavailability.
**Recovery built:** Created a centralized resilience module `backend/core/resilience.py` with `@with_retry`, `@with_retry_sync`, and `@CircuitBreaker` decorators. Applied these to unprotected external HTTP calls across various modules. Added `raise_for_status()` so HTTP errors trigger the resilience logic.
**Blast radius before:** Any temporary network blip or momentary service downtime would cause a failed scan or missed threat detection.
**Watch for:** Other integrations directly using HTTP clients without going through resilience decorators.
