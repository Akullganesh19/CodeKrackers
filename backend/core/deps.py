from typing import List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from backend.core import security
from backend.core.config import settings

# This tells FastAPI to look for the token in the 'Authorization' header.
# The tokenUrl should point to your verification/login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/verify")


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Base dependency to decode the JWT.
    Returns the dictionary of claims (sub, role, exp, etc.)
    """
    try:
        payload = security.decode_token(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid session or expired token",
        )


class RoleChecker:
    """
    Class-based dependency to check for specific roles.
    Usage: Depends(RoleChecker(["admin", "officer"]))
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, payload: Dict[str, Any] = Depends(get_current_token_payload)
    ) -> Dict[str, Any]:
        if payload.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient security clearance for this operation",
            )
        return payload
