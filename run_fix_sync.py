
import os
import psycopg2
import sys

# Ensure backend can be imported
sys.path.append(os.getcwd())

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def fix_schema():
    print("🔧 Checking schema...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Check for meta_key column
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sync_meta' AND column_name='meta_key'")
        if cur.fetchone():
            print("✅ 'meta_key' column exists.")
        else:
            print("⚠️ 'meta_key' is MISSING. Fixing now...")
            # If table exists but no meta_key, it's likely old schema.
            # Best to clear it and add the column.
            cur.execute("DELETE FROM sync_meta")
            cur.execute("ALTER TABLE sync_meta ADD COLUMN meta_key VARCHAR(255)")
            cur.execute("ALTER TABLE sync_meta ADD PRIMARY KEY (meta_key)")
            print("✅ Modified table: Added 'meta_key' and set as PK.")
            
    except Exception as e:
        print(f"❌ Schema check error (likely table missing, will be created by ORM): {e}")

    conn.close()

def run_sync():
    print("\n🚀 Starting Sync to populate metadata...")
    from backend.sync_manager import sync_opportunities
    sync_opportunities()

if __name__ == "__main__":
    fix_schema()
    run_sync()
