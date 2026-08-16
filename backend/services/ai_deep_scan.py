import logging
from typing import Dict, Any
from groq import Groq
from backend.core.config import settings
from backend.services.ollama_scan import ollama_deep_scan
import requests
from backend.core.resilience import with_retry_sync, CircuitBreaker

logger = logging.getLogger("vas.ai_scan")


@CircuitBreaker(failure_threshold=3, recovery_timeout=60)
@with_retry_sync(max_attempts=3, initial_backoff=0.5)
def _call_groq_api(client, prompt):
    return client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a cybersecurity expert specializing in Vishing and Smishing detection."},
            {"role": "user", "content": prompt}
        ],
        model=settings.GROQ_MODEL,
        response_format={"type": "json_object"}
    )

def ai_deep_scan(content: str, source_type: str = "sms") -> Dict[str, Any]:
    """
    Hybrid AI Analysis:
    1. Tries local Ollama (OpenClaw) first for privacy/cost.
    2. Falls back to Groq Cloud (Llama 3.1) if local is unavailable.
    """
    
    # ── Attempt Local Ollama First ──
    try:
        logger.info("Using local Ollama for analysis...")
        local_result = ollama_deep_scan(content, source_type)
        if local_result["score_increase"] > 0:
            return local_result
    except:
        logger.info("Ollama not reachable, falling back to Groq Cloud...")

    # ── Fallback to Groq ──
    if not settings.GROQ_API_KEY:
        return {"score_increase": 0.0, "reason": "AI Scan disabled (No API Key)"}

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        prompt = f"""
        Analyze this {source_type} for potential scam/phishing intent. 
        Content: "{content}"
        
        Provide a JSON response with:
        1. "is_scam": boolean
        2. "confidence": float (0-1)
        3. "reason": string summary
        4. "risk_factors": list of strings
        """

        chat_completion = _call_groq_api(client, prompt)

        import json
        result = json.loads(chat_completion.choices[0].message.content)
        
        return {
            "score_increase": round(result.get("confidence", 0.0), 2) if result.get("is_scam") else 0.0,
            "reason": f"Cloud AI: {result.get('reason', 'Analysis complete')}",
            "risk_factors": result.get("risk_factors", [])
        }
    except Exception as e:
        logger.error(f"Cloud AI Scan Error: {e}")
        return {"score_increase": 0.0, "reason": f"AI Scan failed: {e}"}
