import logging
import requests
import json
from typing import Dict, Any
from backend.core.resilience import CircuitBreaker, with_retry_sync

logger = logging.getLogger("vas.ollama")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b" # Upgraded for tool-calling support

cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

@cb
@with_retry_sync(max_attempts=3, base_delay=0.5)
def _do_ollama_request(payload):
    response = requests.post(OLLAMA_URL, json=payload, timeout=5)
    response.raise_for_status()
    return response

def ollama_deep_scan(content: str, source_type: str = "sms") -> Dict[str, Any]:
    """
    Uses local Ollama instance for on-device/private threat analysis.
    """
    try:
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
        
        response = _do_ollama_request(payload)

        result = response.json().get("response", "{}")
        data = json.loads(result)

        return {
            "score_increase": round(data.get("confidence", 0.0), 2) if data.get("is_scam") else 0.0,
            "reason": data.get("reason", "Local AI Analysis complete"),
            "risk_factors": data.get("risk_factors", [])
        }
            
    except Exception as e:
        logger.error(f"Ollama Scan Error: {e}")
        return {"score_increase": 0.0, "reason": "Local AI Scan failed"}
