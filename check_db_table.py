
import sys
import psycopg2
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

try:
    print(f"Connecting to {DB_URL}...")
    conn = psycopg2.connect(DB_URL)
    print("✅ Connected!")
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.sync_meta');")
    res = cur.fetchone()[0]
    if res:
        print(f"✅ sync_meta table exists: {res}")
    else:
        print("❌ sync_meta table does NOT exist")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
