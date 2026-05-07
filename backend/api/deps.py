"""
Dependency injection for auth, DB sessions, and role-based access control.
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import ALGORITHM
from backend.db.session import get_db
from backend.models.user import User, UserRole
from backend.schemas.token import TokenPayload

logger = logging.getLogger("vas.auth")

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """Decode JWT, validate claims, and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        logger.warning("TOKEN_INVALID: %s", str(e)[:100])
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        logger.warning("TOKEN_USER_NOT_FOUND sub=%s", token_data.sub)
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )
    return current_user


# ─── Role-based Guards ───

def require_role(*roles: UserRole):
    """Factory for role-based dependency injection."""
    def _guard(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            logger.warning(
                "ACCESS_DENIED user=%d role=%s required=%s path=unknown",
                current_user.id,
                current_user.role.value,
                [r.value for r in roles],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _guard


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required",
        )
    return current_user


def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_current_officer_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in {UserRole.OFFICER, UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer or admin privileges required",
        )
    return current_user
