import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import AsyncSessionLocal, engine
from backend.models.orm import User, Base
from backend.core.security import get_password_hash

async def seed_admin():
    async with engine.begin() as conn:
        # Ensure tables exist
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@vsdp.org"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        admin = User(
            email="admin@vsdp.org",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("Admin user created successfully!")
        print("Email: admin@vsdp.org")
        print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(seed_admin())
