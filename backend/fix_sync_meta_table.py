
from sqlalchemy import create_engine, text
from backend.app.core.database import DATABASE_URL
from backend.app.models import Base, SyncMeta

def fix_sync_meta():
    engine = create_engine(DATABASE_URL)
    
    print("🗑️ Dropping 'sync_meta' table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS sync_meta"))
        conn.commit()
    
    print("✨ Recreating 'sync_meta' table from model...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")

if __name__ == "__main__":
    fix_sync_meta()
