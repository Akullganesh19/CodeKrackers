import httpx
import re
from backend.core.config import settings
from backend.core.resilience import with_retries, circuit_breaker, CircuitBreaker

_crypto_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)

def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)

@circuit_breaker(_crypto_breaker)
@with_retries(max_attempts=3, base_delay=0.1)
async def check_crypto_honeypot(address: str) -> dict:
    """
    Check if a crypto address/token is a honeypot using honeypot.is API.
    """
    api_key = getattr(settings, "HONEYPOT_IS_API_KEY", None)
    if not api_key:
        raise ValueError("Honeypot.is API key not configured")

    url = "https://api.honeypot.is/v2/IsHoneypot"
    headers = {"X-API-KEY": api_key}
    params = {"address": address}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()
