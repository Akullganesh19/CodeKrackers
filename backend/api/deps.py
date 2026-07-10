from typing import AsyncGenerator, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import security
from ..core.database import AsyncSessionLocal, SessionLocal
from ..models.orm import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


def get_db_sync() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    payload = security.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(get_current_token_payload),
) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # First try lookup by primary key (real JWTs store str(user.id) as sub)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # Fallback: lookup by email (dev dummy_token stores email as sub)
    if not user:
        result = await db.execute(select(User).where(User.email == user_id))
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


async def get_current_officer_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in [
        UserRole.OFFICER,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
    ]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
