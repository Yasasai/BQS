
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import SyncMeta


def read_sync_meta():
    db = SessionLocal()
    with open("sync_status_recheck.txt", "w", encoding="utf-8") as f:
        try:
            f.write("🔹 Reading SyncMeta table...\n")
            meta = db.query(SyncMeta).filter(SyncMeta.meta_key == "oracle_opportunities").first()
            if meta:
                f.write(f"✅ Found SyncMeta for 'oracle_opportunities'\n")
                f.write(f"   Last Sync: {meta.last_sync_timestamp}\n")
                f.write(f"   Status: {meta.sync_status}\n")
                f.write(f"   Records Processed: {meta.records_processed}\n")
            else:
                f.write("❌ No SyncMeta found for 'oracle_opportunities'\n")
        except Exception as e:
            f.write(f"❌ Error: {e}\n")
        finally:
            db.close()

if __name__ == "__main__":
    read_sync_meta()
