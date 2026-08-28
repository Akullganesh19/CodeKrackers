## 2024-05-22 — Protect local AI dependencies (Ollama and OpenClaw)
**Failure point found:** `requests.post(OLLAMA_URL)` in `ollama_scan.py`, `requests.get(OPENCLAW_URL)` in `openclaw_agent.py`, and `requests.get("http://localhost:11434")` in `ai_deep_scan.py` were fully unprotected.
**Why it existed:** Assumed local endpoints would always be up and instantaneous.
**Recovery built:** Extracted `requests` calls into `_do_request` helper functions and wrapped them with `@CircuitBreaker` and `@with_retry_sync`.
**Blast radius before:** Hard crashes, delayed fallbacks, and connection exhaustion during transient local server instability.
**Watch for:** Other `requests.get` or `requests.post` scattered in new services that talk to external APIs without decorators.
