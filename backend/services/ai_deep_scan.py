import logging
from typing import Dict, Any
from groq import Groq
from backend.core.config import settings
from backend.services.ollama_scan import ollama_deep_scan
from backend.core.resilience import CircuitBreaker, with_retry_sync
import requests
import json

logger = logging.getLogger("vas.ai_scan")


def groq_fallback(content: str, source_type: str) -> Dict[str, Any]:
    logger.warning("Groq fallback executed.")
    return {"score_increase": 0.0, "reason": "AI Scan failed"}


@CircuitBreaker(fallback=groq_fallback)
@with_retry_sync(max_attempts=3)
def call_groq(content: str, source_type: str) -> Dict[str, Any]:
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

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a cybersecurity expert specializing in Vishing and Smishing detection.",
            },
            {"role": "user", "content": prompt},
        ],
        model=settings.GROQ_MODEL,
        response_format={"type": "json_object"},
    )

    result = json.loads(chat_completion.choices[0].message.content)

    return {
        "score_increase": (
            round(result.get("confidence", 0.0), 2) if result.get("is_scam") else 0.0
        ),
        "reason": f"Cloud AI: {result.get('reason', 'Analysis complete')}",
        "risk_factors": result.get("risk_factors", []),
    }


def ai_deep_scan(content: str, source_type: str = "sms") -> Dict[str, Any]:
    """
    Hybrid AI Analysis:
    1. Tries local Ollama (OpenClaw) first for privacy/cost.
    2. Falls back to Groq Cloud (Llama 3.1) if local is unavailable.
    """

    # ── Attempt Local Ollama First ──
    try:
        # Quick check if Ollama is running
        requests.get("http://localhost:11434", timeout=1)
        logger.info("Using local Ollama for analysis...")
        local_result = ollama_deep_scan(content, source_type)
        if local_result["score_increase"] > 0:
            return local_result
    except:
        logger.info("Ollama not reachable, falling back to Groq Cloud...")

    # ── Fallback to Groq ──
    if not settings.GROQ_API_KEY:
        return {"score_increase": 0.0, "reason": "AI Scan disabled (No API Key)"}

    return call_groq(content, source_type)
