import asyncio
import uuid
import threading
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from backend.models.orm import Base, Blacklist as BlacklistEntry, BlacklistType
from backend.services.threat_intel import auto_blacklist

# Use a file-based SQLite db for concurrency (in-memory sqlite doesn't handle multiple threads well without pool config)
engine = create_engine("sqlite:///test_concurrency.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def worker(identifier, identifier_type):
    db = SessionLocal()
    auto_blacklist(db, identifier, identifier_type, "test reason")
    db.close()

def run_test():
    db = SessionLocal()
    identifier = "1234567890"
    identifier_type = BlacklistType.PHONE

    # ensure clean state
    db.query(BlacklistEntry).filter_by(value=identifier).delete()
    db.commit()

    # insert initial
    entry = BlacklistEntry(type=identifier_type, value=identifier, report_count=1, confidence=0.5, reason="initial")
    db.add(entry)
    db.commit()
    db.close()

    # run concurrent updates
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker, args=(identifier, identifier_type))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    db = SessionLocal()
    final_entry = db.query(BlacklistEntry).filter_by(value=identifier).first()
    print(f"Final report_count: {final_entry.report_count} (Expected: 11)")
    db.close()

if __name__ == "__main__":
    run_test()
