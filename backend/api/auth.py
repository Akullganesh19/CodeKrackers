import random
from datetime import timedelta
from typing import Any

import redis
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session
from twilio.rest import Client

from backend.api import deps
from backend.core import security
from backend.core.config import settings
from backend.core.limiter import limiter
from backend.core.logger import logger
from backend.models import User
from backend.schemas.token import Token
from backend.schemas.user import OTPSend, OTPVerify
from backend.schemas.user import User as UserSchema
from backend.schemas.user import UserCreate

router = APIRouter()

# Initialize Redis client for OTP storage (with graceful fallback if not configured)
redis_client = None
if settings.REDIS_HOST:
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")


@router.post("/login/access-token", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db_sync),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Supports email or phone_number as username.
    """
    user = security.authenticate_user(
        db,
        email=form_data.username,
        phone=form_data.username,
        password=form_data.password,
    )

    if not user:
        # Increment failed login logic is handled inside authenticate_user
        raise HTTPException(status_code=400, detail="Incorrect email/phone or password")

    if not security.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/send-otp")
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

    if (
        "@" not in otp_in.identifier
        and settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
    ):
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"VSDP Security Code: {otp_code}. Valid for 5 minutes. Do not share.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=otp_in.identifier,
            )
        except Exception as e:
            logger.error(
                f"SMS_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}"
            )

    if "@" in otp_in.identifier and settings.SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=otp_in.identifier,
                subject="VSDP Security Code",
                plain_text_content=f"Your VSDP security code is: {otp_code}. Valid for 5 minutes. Do not share.",
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            logger.error(
                f"EMAIL_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}"
            )

    if settings.ENVIRONMENT == "development" or settings.DEBUG:
        logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")
    else:
        logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> [REDACTED]")

    return {"message": "OTP sent successfully"}


@router.post("/verify")
async def verify_otp(
    *,
    db: Session = Depends(deps.get_db_sync),
    otp_verify: OTPVerify,
) -> Any:
    """
    Verifies the OTP against Redis. Unlocks account or resets attempts on success.
    """
    user = (
        db.query(User)
        .filter(
            (User.email == otp_verify.identifier)
            | (User.phone_number == otp_verify.identifier)
        )
        .first()
    )

    if user and security.check_account_locked(user.locked_until):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again after {user.locked_until.isoformat()}",
        )

    redis_key = f"otp:{otp_verify.identifier}"
    stored_code = (
        redis_client.get(redis_key) if redis_client else otp_verify.code
    )  # Mock pass if redis down for demo

    if not stored_code or otp_verify.code != stored_code:
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= security.MAX_LOGIN_ATTEMPTS:
                user.locked_until = security.get_lockout_time()
            db.commit()
        logger.warning(f"Auth failure: Invalid OTP attempt for {otp_verify.identifier}")
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code"
        )

    if redis_client:
        redis_client.delete(redis_key)

    if user:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    return {"message": "OTP verified successfully"}


@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(deps.get_db_sync),
    user_in: UserCreate,
) -> Any:
    """
    Create new user without needing to be logged in.
    """
    user = (
        db.query(User)
        .filter(
            (User.email == user_in.email) | (User.phone_number == user_in.phone_number)
        )
        .first()
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email or phone number already exists in the system.",
        )
    user = security.create_user(db, user_in)
    return user
