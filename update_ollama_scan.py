import re

with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()

import_stmt = "from backend.core.resilience import with_retries, circuit_breaker\n"
if "from backend.core.resilience" not in content:
    content = content.replace("from typing import Dict, Any", "from typing import Dict, Any\n" + import_stmt)

helpers = """
@with_retries(max_attempts=2, base_delay=0.2)
@circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
def _call_ollama_api(payload: dict) -> dict:
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    response.raise_for_status() # Raise error for bad status codes so retries can catch it
    return response.json()

"""
if "_call_ollama_api" not in content:
    content = content.replace("def ollama_deep_scan", helpers + "def ollama_deep_scan")


search_str = """        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json().get("response", "{}")
            data = json.loads(result)

            return {
                "score_increase": round(data.get("confidence", 0.0), 2) if data.get("is_scam") else 0.0,
                "reason": data.get("reason", "Local AI Analysis complete"),
                "risk_factors": data.get("risk_factors", [])
            }
        else:
            logger.warning(f"Ollama returned status {response.status_code}")
            return {"score_increase": 0.0, "reason": "Ollama service unavailable"}"""

replace_str = """        try:
            response_json = _call_ollama_api(payload)
            result = response_json.get("response", "{}")
            data = json.loads(result)

            return {
                "score_increase": round(data.get("confidence", 0.0), 2) if data.get("is_scam") else 0.0,
                "reason": data.get("reason", "Local AI Analysis complete"),
                "risk_factors": data.get("risk_factors", [])
            }
        except Exception as e:
            logger.warning(f"Ollama service call failed: {e}")
            raise e # re-raise to be caught by outer try-except and return default fallback"""

content = content.replace(search_str, replace_str)

with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)
