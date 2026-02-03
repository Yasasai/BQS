
import os
import psycopg2
from sqlalchemy import create_engine
from backend.app.models import Base

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def fix_table():
    print("Beginning Table Fix...")
    try:
        # 1. Drop existing table via raw SQL to be sure
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("Dropping 'sync_meta' table if exists...")
        cur.execute("DROP TABLE IF EXISTS sync_meta CASCADE;")
        conn.close()
        print("✅ Dropped 'sync_meta'.")

        # 2. Recreate using SQLAlchemy
        print("Recreating table from model...")
        engine = create_engine(DB_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ Recreated tables (including sync_meta).")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")

if __name__ == "__main__":
    fix_table()
