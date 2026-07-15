## YYYY-MM-DD — Global Network Resiliency
**Failure point found:** Core external network calls (Twilio, SendGrid, Redis, Ollama, Groq, OpenClaw) were made synchronously with no retry logic or circuit breakers. A single slow API or temporary offline service could cascade into failures or long request times.
**Why it existed:** Quick implementation for MVP; network reliability was assumed.
**Recovery built:**
- A custom `CircuitBreaker` and `with_retries` decorator in `backend/core/resilience.py` with exponential backoff.
- Applied self-healing mechanisms to Twilio SMS and SendGrid email sending logic, including offloading blocking calls using `asyncio.get_running_loop().run_in_executor()`.
- Added circuit breakers to `ollama_deep_scan`, `check_ollama_status`, `call_groq_api`, `openclaw_analysis`, and `mythos_engine.deep_analyze`.
- Handled Redis timeouts safely in `auth.py`.
**Blast radius before:** High. Any network hiccup in external services would lead to 500 errors and block users from authenticating or processing threat analysis.
**Watch for:** Other areas where third party services might be added directly in endpoints without going through the resilience wrappers.
