import logging
import requests
import json
from typing import Dict, Any
from backend.core.resilience import with_retries, circuit_breaker

logger = logging.getLogger("vas.ollama")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b" # Upgraded for tool-calling support

@circuit_breaker(max_failures=3, reset_timeout=60)
@with_retries(max_attempts=3, base_delay=1.0, exceptions=(requests.RequestException,))
def ollama_deep_scan(content: str, source_type: str = "sms") -> Dict[str, Any]:
    """
    Uses local Ollama instance for on-device/private threat analysis.
    Raises exception on failure to trigger retries and circuit breaking.
    """
    prompt = f"""
    Analyze this {source_type} for scam/phishing intent.
    Content: "{content}"

    Respond ONLY with a JSON object:
    {{
        "is_scam": boolean,
        "confidence": float (0.0 to 1.0),
        "reason": "short summary",
        "risk_factors": ["list"]
    }}
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=10)
    response.raise_for_status()

    result = response.json().get("response", "{}")
    data = json.loads(result)

    return {
        "score_increase": round(data.get("confidence", 0.0), 2) if data.get("is_scam") else 0.0,
        "reason": data.get("reason", "Local AI Analysis complete"),
        "risk_factors": data.get("risk_factors", [])
    }
