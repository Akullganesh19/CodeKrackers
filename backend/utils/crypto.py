import httpx
import re
from backend.core.config import settings
from backend.core.resilience import async_circuit_breaker, async_with_retries

def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)

async def check_crypto_honeypot_fallback(*args, **kwargs) -> dict:
    return {"error": "Honeypot.is API unavailable (Circuit Breaker OPEN)"}

@async_circuit_breaker(failure_threshold=3, recovery_timeout=60.0, fallback_factory=check_crypto_honeypot_fallback)
@async_with_retries(max_attempts=2, base_delay=0.1)
async def check_crypto_honeypot(address: str) -> dict:
    """
    Check if a crypto address/token is a honeypot using honeypot.is API.
    """
    api_key = getattr(settings, "HONEYPOT_IS_API_KEY", None)
    if not api_key:
        return {"error": "Honeypot.is API key not configured"}

    url = "https://api.honeypot.is/v2/IsHoneypot"
    headers = {"X-API-KEY": api_key}
    params = {"address": address}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"API returned status {response.status_code}")
