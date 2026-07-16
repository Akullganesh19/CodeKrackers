import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.base import Base  # noqa
from backend.db.session import engine  # noqa
from backend.core.config import settings


def migrate():
    print(f"Connecting to: {settings.DATABASE_URL.split('@')[-1]}")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        db_type = (
            "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL/Supabase"
        )
        print(f"[SUCCESS] Tables created successfully in {db_type}!")
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")


if __name__ == "__main__":
    if "[PASSWORD]" in settings.DATABASE_URL:
        print(
            "⚠️  Please update your DATABASE_URL in .env with your actual Supabase credentials first."
        )
    else:
        migrate()
