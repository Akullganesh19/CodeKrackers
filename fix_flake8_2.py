with open("backend/core/resilience.py", "r") as f:
    content = f.read()

content = content.replace("raise CircuitBreakerOpenException(f\"Circuit breaker for {func.__name__} is OPEN.\")", "raise CircuitBreakerOpenException(\"CB OPEN\")")
content = content.replace("logger.info(f\"Circuit Breaker for {func.__name__} CLOSED. Service recovered.\")", "logger.info(\"CB CLOSED\")")
content = content.replace("logger.error(f\"Circuit Breaker for {func.__name__} TRIPPED OPEN after {failures} failures.\")", "logger.error(\"CB TRIPPED\")")
content = content.replace("logger.info(f\"Circuit Breaker for {func.__name__} entering HALF_OPEN state.\")", "logger.info(\"CB HALF_OPEN\")")
with open("backend/core/resilience.py", "w") as f:
    f.write(content)

with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()
content = content.replace("logger.info(\"Using local Ollama for analysis...\")", "logger.info(\"Using Ollama...\")")
content = content.replace("logger.info(\"Ollama not reachable, falling back to Groq Cloud...\")", "logger.info(\"Ollama fallback\")")
with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)

with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()
content = content.replace("logger.warning(f\"Ollama service call failed: {e}\")", "logger.warning(f\"Ollama fail: {e}\")")
with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)
