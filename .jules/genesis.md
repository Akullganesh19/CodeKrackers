## 2024-09-04 — External API Resilience Built

**Failure point found:** External API integrations (Groq Cloud LLM, local Ollama, Twilio SMS) lacked resilience. They were making single-attempt requests and failing fast.
**Why it existed:** Quick implementation for hackathon MVP. Focus was on happy-path functionality rather than robustness under transient failures (network blips, rate limits, temporary unavailability).
**Recovery built:** Created a core `CircuitBreaker` and synchronous exponential backoff retry mechanism (`with_retry_sync`). Wrapped all third-party external calls across `ai_deep_scan`, `ollama_scan`, `notifier`, and `sms` utilities.
**Blast radius before:** A single timeout from Groq or Twilio would immediately fail a user's action, degrade threat detection, or prevent OTP delivery without auto-recovery.
**Watch for:** Other areas where external network calls are introduced, ensuring they use the core resilience decorators. Also watch out for async IO paths which would need an async version of the retry decorator.