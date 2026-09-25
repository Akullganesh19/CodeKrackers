import random
from datetime import datetime, timedelta, timezone
from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api import deps
from backend.core import security
from backend.core.config import settings
from backend.models.user import User
from backend.schemas.user import User as UserSchema
from backend.schemas.user import UserCreate, UserRegister
from backend.schemas.token import Token
from backend.schemas.otp import OTPSend, OTPVerify
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.db.session import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserRegister,
) -> Any:
    """
    Register a new user. Default role is Citizen.
    """
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    if db.query(User).filter(User.phone == user_in.phone).first():
        raise HTTPException(
            status_code=400,
            detail="The user with this phone number already exists in the system.",
        )

    user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="Citizen",  # Always force to Citizen on registration
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/otp/send")
async def send_otp(
    *,
    db: Session = Depends(deps.get_db),
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
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"VSDP Security Code: {otp_code}. Valid for 5 minutes. Do not share.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=otp_in.identifier
            )
        except Exception as e:
            logger.error(f"SMS_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")

    elif "@" in otp_in.identifier and settings.SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=otp_in.identifier,
                subject='VSDP Security Code',
                plain_text_content=f"Your VSDP security code is: {otp_code}. Valid for 5 minutes. Do not share."
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            logger.error(f"EMAIL_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")

    logger.info(f"SECURITY: Generated OTP for {otp_in.identifier} -> {otp_code}")
    
    return {"message": "OTP sent successfully"}

@router.post("/verify")
async def verify_otp(
    *,
    db: Session = Depends(deps.get_db),
    otp_verify: OTPVerify,
) -> Any:
    """
    Verify OTP and return a JWT token.
    """
    # Rate limit check on identifier
    user = db.query(User).filter((User.email == otp_verify.identifier) | (User.phone == otp_verify.identifier)).first()

    if user and user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again after {user.locked_until.isoformat()}"
        )

    redis_key = f"otp:{otp_verify.identifier}"
    stored_code = redis_client.get(redis_key) if redis_client else "123456" # Mock pass if redis down for demo

    if not stored_code or otp_verify.code != stored_code.decode('utf-8') if isinstance(stored_code, bytes) else stored_code:
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= security.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                logger.warning(f"SECURITY: Account locked due to max failed OTPs for {otp_verify.identifier}")
            db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Success
    if redis_client:
        redis_client.delete(redis_key)

    if user:
        user.failed_login_attempts = 0
        db.commit()
    else:
        # If user doesn't exist, we might auto-create a shadow profile or reject
        pass

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id if user else "anonymous", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
