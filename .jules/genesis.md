## YYYY-MM-DD — Circuit Breakers and Auto-Retries for External APIs
**Failure point found:** External API calls to Groq, Ollama, and OpenClaw gateways were lacking resiliency, making them vulnerable to transient network failures, timeouts, and outages, which would cause direct failures for user requests.
**Why it existed:** The backend was designed for "happy path" synchronous requests, assuming external endpoints were always 100% available and ignoring standard distributed systems failure modes.
**Recovery built:** Implemented `@CircuitBreaker` and `@with_retry_sync` decorators with exponential backoff on Groq, Ollama, and OpenClaw requests to automatically retry on transient errors and short-circuit traffic on sustained outages. Also added a health endpoint to monitor their statuses.
**Blast radius before:** Any transient timeout or temporary unavailability of Groq, local Ollama, or OpenClaw would instantly fail the API request and result in dropped detections.
**Watch for:** Other external synchronous calls (like database connections or webhook dispatchers) that might lack timeout or retry logic.
