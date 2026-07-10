from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.orm import User
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """
    BYPASS MODE: Returns the admin user automatically without checking tokens.
    """
    result = await db.execute(select(User).where(User.email == "admin@vsdp.org"))
    user = result.scalar_one_or_none()

    if user is None:
        # Fallback if DB is empty
        user = User(
            email="admin@vsdp.org", role="admin", rbac_level=4, full_name="Auto Admin"
        )
    return user


def require_role(min_rbac_level: int):
    """
    Dependency factory to enforce RBAC levels (e.g., Officer level 3+).
    """

    def role_checker(user: User = Depends(get_current_user)):
        if user.rbac_level < min_rbac_level:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions for this operation"
            )
        return user

    return role_checker
