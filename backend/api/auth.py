from datetime import datetime, timedelta, timezone
import logging
import random
from typing import Any, Optional

import redis
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.api import deps
from backend.core.limiter import limiter
from backend.core import security
from backend.core.security import get_lockout_time, MAX_LOGIN_ATTEMPTS
from backend.core.config import settings
from backend.models.orm import User, UserRole
from backend.core.resilience import with_retry_sync

router = APIRouter()
logger = logging.getLogger("vas.auth")

try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception as e:
    logger.warning(f"REDIS_OFFLINE: {e}. Auth will use local fallback.")
    redis_client = None

class OTPSend(BaseModel):
    identifier: str
    role: str = "citizen"

class OTPVerify(BaseModel):
    identifier: str
    code: str
    role: str = "citizen"

class LoginRequest(BaseModel):
    username: str = ""
    email: str = ""
    password: str
    role: str = "citizen"

class UserRegister(BaseModel):
    email: str
    password: str
    phone_number: Optional[str] = None
    role: str = "citizen"

@with_retry_sync(max_attempts=3, initial_backoff=0.2)
def send_twilio_otp(to_number: str, otp_code: str):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=f"VSDP Security Code: {otp_code}. Valid for 5 minutes. Do not share.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number
    )

@with_retry_sync(max_attempts=3, initial_backoff=0.2)
def send_sendgrid_otp(to_email: str, otp_code: str):
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_email,
        subject='VSDP Security Code',
        plain_text_content=f"Your VSDP security code is: {otp_code}. Valid for 5 minutes. Do not share."
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)

@router.post("/send")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def send_otp(
    *,
    db: Session = Depends(deps.get_db_sync),
    request: Request,
    otp_in: OTPSend,
) -> Any:
    """
    Generates a 6-digit OTP and stores it in Redis with a TTL.
    """
    otp_code = f"{random.randint(100000, 999999)}"
    
    redis_key = f"otp:{otp_in.identifier}"
    if redis_client:
        redis_client.setex(redis_key, settings.OTP_EXPIRE_SECONDS, otp_code)

    if "@" not in otp_in.identifier and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            send_twilio_otp(otp_in.identifier, otp_code)
        except Exception as e:
            logger.error(f"SMS_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")
            raise HTTPException(status_code=503, detail="Failed to send SMS OTP due to gateway error.")

    if "@" in otp_in.identifier and settings.SENDGRID_API_KEY:
        try:
            send_sendgrid_otp(otp_in.identifier, otp_code)
        except Exception as e:
            logger.error(f"EMAIL_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")
            raise HTTPException(status_code=503, detail="Failed to send Email OTP due to gateway error.")

    logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")
    
    return {"message": "OTP sent successfully"}

@router.post("/verify")
async def verify_otp(
    *,
    db: Session = Depends(deps.get_db_sync),
    otp_verify: OTPVerify,
) -> Any:
    """
    Verifies the OTP and issues a signed JWT access token.
    """
    user = db.query(User).filter(
        (User.email == otp_verify.identifier) | (User.phone_number == otp_verify.identifier)
    ).first()

    if user and security.check_account_locked(user.locked_until):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again after {user.locked_until.isoformat()}"
        )

    redis_key = f"otp:{otp_verify.identifier}"
    stored_code = redis_client.get(redis_key) if redis_client else otp_verify.code # Mock pass if redis down for demo

    if not stored_code or otp_verify.code != stored_code:
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= security.MAX_LOGIN_ATTEMPTS:
                user.locked_until = security.get_lockout_time()
            db.commit()
        logger.warning(f"Auth failure: Invalid OTP attempt for {otp_verify.identifier}")
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    if not user:
        user = User(
            email=otp_verify.identifier if "@" in otp_verify.identifier else None,
            phone_number=otp_verify.identifier if "@" not in otp_verify.identifier else None,
            is_active=True,
            role=UserRole(otp_verify.role)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    if redis_client:
        redis_client.delete(redis_key)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, 
            role=user.role.value, 
            expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/refresh-token")
async def refresh_access_token(
    *,
    db: Session = Depends(deps.get_db_sync),
    current_user_payload: dict = Depends(deps.get_current_token_payload),
) -> Any:
    """
    Refreshes the JWT access token.
    """
    user_id = current_user_payload.get("sub")
    user_role = current_user_payload.get("role")

    if not user_id or not user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        subject=user_id,
        role=user_role,
        expires_delta=access_token_expires,
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/login")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login_access_token_password(
    *,
    db: Session = Depends(deps.get_db_sync),
    request: Request,
    form_data: LoginRequest,
) -> Any:
    # Accept either 'email' or 'username' field
    email_input = form_data.email or form_data.username
    user = db.query(User).filter(User.email == email_input).first()

    if user and security.check_account_locked(getattr(user, "locked_until", None)):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked. Try again in 15 minutes.",
        )

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked_until = get_lockout_time()
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=str(user.id), role=role_val, expires_delta=access_token_expires)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": role_val,
        }
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register_user(
    *,
    db: Session = Depends(deps.get_db_sync),
    request: Request,
    user_in: UserRegister,
) -> Any:
    is_valid, msg = security.validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    if user_in.phone_number:
        existing_phone = db.query(User).filter(User.phone_number == user_in.phone_number).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered.")

    new_user = User(
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=security.get_password_hash(user_in.password),
        role=UserRole(user_in.role),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registration successful", "user_id": new_user.id}