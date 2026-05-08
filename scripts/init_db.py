import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import sync_engine
from backend.models.orm import Base

def init_db():
    print("Initializing Database...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database Tables Created Successfully!")

if __name__ == "__main__":
    init_db()
