
import sys
import os
from sqlalchemy import create_engine, text
from backend.app.core.database import DATABASE_URL
from backend.app.models import Base as AppBase

# Add current directory to path to import batch_sync_with_offset
sys.path.append(os.getcwd())
# We need to be careful about relative imports inside batch_sync_with_offset if any,
# but checking the file, it uses standard library and sqlalchemy, so it should be fine.
try:
    import batch_sync_with_offset
except ImportError:
    # If standard import fails, try appending the full path
    sys.path.append(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
    import batch_sync_with_offset

def fix_schema():
    print(f"Connecting to: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    print("🗑️ Dropping problematic tables...")
    with engine.connect() as conn:
        # We use CASCADE to drop dependent objects if any
        conn.execute(text("DROP TABLE IF EXISTS sync_meta CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS sync_state CASCADE"))
        conn.commit()
    
    print("✨ Recreating 'sync_meta' from AppBase...")
    # This will create sync_meta and other missing tables from AppBase
    AppBase.metadata.create_all(bind=engine)
    
    print("✨ Recreating 'sync_state' from BatchSyncBase...")
    # This will create sync_state and minimal_opportunities if missing
    batch_sync_with_offset.Base.metadata.create_all(bind=engine)
    
    print("✅ Schema fixed successfully.")

if __name__ == "__main__":
    fix_schema()
