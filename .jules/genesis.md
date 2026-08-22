## 2024-08-22 — AI Scan External Calls

**Failure point found:** External API requests in `backend/services/ollama_scan.py`, `backend/services/ai_deep_scan.py`, and `backend/services/openclaw_agent.py` to Local Ollama, Groq Cloud, and OpenClaw models lacked retry on transient failures and circuit breaking on sustained outages.
**Why it existed:** The backend directly invoked `requests.post`/`requests.get` or the Groq client `client.chat.completions.create` inline within services, depending on solitary `try/except` blocks to handle network unreliability, providing no resilience.
**Recovery built:** Created `backend/core/resilience.py` with `@with_retry_sync`, `@with_retry`, and `@CircuitBreaker` decorators. These were applied to new extracted global helper functions in each service to automatically backoff-retry (3 attempts, 0.5s base delay) and short-circuit after 3 consecutive failures (60s cooldown).
**Blast radius before:** Any network stutter or AI service transient timeout caused an immediate complete feature failure (silent exception logging) for the user's specific request. Repeated failures continuously blocked event loop/threads with pointless timeout waiting.
**Watch for:** Other integrations utilizing `requests` (e.g. database connections, external webhooks) lacking these primitive protections.
