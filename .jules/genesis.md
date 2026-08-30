## 2024-06-25 — [Resilient AI Inference Calls]

**Failure point found:** External API calls to Groq (`client.chat.completions.create`) and Ollama (`requests.post`) were unprotected against transient network failures and timeouts. A single failure would immediately bubble up and fail the current execution context.

**Why it existed:** The AI integration logic was initially built assuming high availability and instant responses from these external services. Simple `try-except` blocks were used for logging and returning fallback dictionaries, but there was no attempt to retry transient issues or prevent continuous failing calls (cascading failure).

**Recovery built:**
1. Added a global resilience module (`backend/core/resilience.py`) providing exponential backoff retries (`@with_retry_sync`, `@with_retry`) and a thread-safe `@CircuitBreaker`.
2. Extracted the Groq and Ollama API calls into dedicated functions (`_do_groq_request` and `_do_ollama_request`) and wrapped them with these decorators.
3. The outer functions now correctly catch the raised exceptions (if the retry block is exhausted or the circuit is OPEN) and return their original fallback dictionaries.

**Blast radius before:** Any temporary API blip, network partition, or brief LLM timeout would cause an immediate fallback, meaning the threat scan would return a 0.0 confidence score (essentially a silent failure to detect a threat) for that specific message.

**Watch for:** Other external dependencies, such as database calls (which are often synchronous and block the event loop in `FastAPI`), webhook dispatches, or notification calls (e.g., Twilio/SendGrid). We need to ensure they also use resilience patterns where appropriate.
