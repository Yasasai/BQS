
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import DATABASE_URL
from backend.app.models import SyncMeta
from datetime import datetime

def test_sync_meta_insert():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        print("Attempting to upsert SyncMeta...")
        meta = session.query(SyncMeta).filter(SyncMeta.meta_key == "test_key").first()
        if not meta:
            meta = SyncMeta(meta_key="test_key")
            session.add(meta)
        
        meta.last_sync_timestamp = datetime.utcnow()
        meta.sync_status = "SUCCESS"
        meta.records_processed = 100
        
        session.commit()
        print("✅ SyncMeta upsert successful!")
    except Exception as e:
        print(f"❌ SyncMeta failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_sync_meta_insert()
