"""
Authentication endpoint with brute-force protection and audit logging.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api import deps
from backend.core import security
from backend.core.events import EventBus
from backend.core.config import settings
from backend.core.limiter import limiter
from backend.models import User
from backend.schemas.token import Token

logger = logging.getLogger("vas.auth")
router = APIRouter()


@router.post("/login/access-token", response_model=Token)
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db_sync),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 login with brute-force protection:
    - 5 failed attempts → 15-minute lockout
    - Audit logging on every attempt
    - Constant-time comparison to prevent timing attacks
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    # Check if account is locked
    if user and security.check_account_locked(getattr(user, "locked_until", None)):
        logger.warning(
            "LOGIN_BLOCKED account locked email=%s ip=%s",
            form_data.username,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to too many failed attempts. Try again in 15 minutes.",
        )

    # Validate credentials
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # Increment failed attempts
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= security.MAX_LOGIN_ATTEMPTS:
                user.locked_until = security.get_lockout_time()
                EventBus.publish("user.account_locked", user_email=user.email, failed_attempts=user.failed_login_attempts, ip_address=request.client.host if "request" in locals() and hasattr(request, "client") and request.client else "unknown")
                logger.critical(
                    "ACCOUNT_LOCKED email=%s attempts=%d ip=%s",
                    form_data.username,
                    user.failed_login_attempts,
                    request.client.host if request.client else "unknown",
                )
            db.commit()

        logger.warning(
            "LOGIN_FAILED email=%s ip=%s",
            form_data.username,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    # Success: reset failed attempts, update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        scopes=[user.role.value],
    )

    logger.info(
        "LOGIN_SUCCESS email=%s role=%s ip=%s",
        user.email,
        user.role.value,
        request.client.host if request.client else "unknown",
    )

    return {"access_token": token, "token_type": "bearer"}
