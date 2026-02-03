
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import init_db, SessionLocal
from backend.app.models import SyncMeta

def verify_sync_meta():
    print("🔹 Initializing DB (should create sync_meta table)...")
    init_db()
    
    db = SessionLocal()
    try:
        print("🔹 Checking if sync_meta table works...")
        # Try to insert/update a dummy record
        meta = db.query(SyncMeta).filter(SyncMeta.meta_key == "test_verification").first()
        if not meta:
            meta = SyncMeta(meta_key="test_verification")
            db.add(meta)
        
        meta.last_sync_timestamp = datetime.utcnow()
        meta.sync_status = "TEST_SUCCESS"
        meta.records_processed = 999
        db.commit()
        
        # Read it back
        saved = db.query(SyncMeta).filter(SyncMeta.meta_key == "test_verification").first()
        if saved:
            print(f"✅ success! Read back: {saved.meta_key}, {saved.last_sync_timestamp}, {saved.sync_status}")
        else:
            print("❌ Failed to read back record.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_sync_meta()
