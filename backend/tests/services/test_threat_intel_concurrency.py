import pytest
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.blacklist import BlacklistType
from backend.models.blacklist import BlacklistEntry
from backend.services.threat_intel import auto_blacklist

# Use a file-based SQLite database for concurrent connections
engine = create_engine("sqlite:///test_concurrent.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_database():
    import backend.models.blacklist # Ensure models are loaded
    from backend.db.base_class import Base
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("test_concurrent.db"):
        os.remove("test_concurrent.db")

def test_auto_blacklist_concurrency(setup_database):
    import backend.services.threat_intel
    # Monkeypatch to use correct model since the code imports from orm.py incorrectly
    backend.services.threat_intel.BlacklistEntry = BlacklistEntry

    db = TestingSessionLocal()
    # Ensure it's empty
    db.query(BlacklistEntry).delete()
    db.commit()

    # Pre-insert
    entry = auto_blacklist(
        db=db,
        identifier="1234567890",
        identifier_type=BlacklistType.PHONE,
        reason="Initial report",
        confidence=0.5
    )
    assert entry.report_count == 1
    db.close()

    # Now simulate 10 concurrent requests reporting the same number
    def report_concurrently():
        thread_db = TestingSessionLocal()
        auto_blacklist(
            db=thread_db,
            identifier="1234567890",
            identifier_type=BlacklistType.PHONE,
            reason="Concurrent report",
        )
        thread_db.close()

    threads = []
    for _ in range(10):
        t = threading.Thread(target=report_concurrently)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Check the final count
    db = TestingSessionLocal()
    final_entry = db.query(BlacklistEntry).filter_by(value="1234567890").first()

    # We expect 1 initial + 10 concurrent = 11
    assert final_entry.report_count == 11, f"Expected 11, got {final_entry.report_count}. Race condition detected!"
    db.close()
