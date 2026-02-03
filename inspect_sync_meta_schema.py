
import os
import psycopg2

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def inspect_table():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        print("Existing columns in sync_meta:")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'sync_meta';
        """)
        rows = cur.fetchall()
        if not rows:
            print("  (Table not found in information_schema, but user says it exists?)")
        for row in rows:
            print(f" - {row[0]} ({row[1]})")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_table()
