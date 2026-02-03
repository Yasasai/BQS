
import os
import psycopg2
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import init_db

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def reset_table():
    print("☢️ Dropping sync_meta table...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS sync_meta CASCADE;")
        conn.close()
        print("✅ Drop successful.")
        
        print("🔄 Re-initializing database to recreate table...")
        init_db()
        print("✅ Re-init complete.")
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")

if __name__ == "__main__":
    reset_table()
