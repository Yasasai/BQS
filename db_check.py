import psycopg2
import sys

def diagnostic():
    db_url = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
    print(f"Attempting to connect to {db_url}...")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
        print("CONNECTED!")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM opportunity")
        print(f"Total Opportunities: {cur.fetchone()[0]}")
        
        cur.execute("SELECT opp_name, workflow_status FROM opportunity WHERE is_active=true LIMIT 5")
        print("Sample Active Opps:", cur.fetchall())
        
        conn.close()
    except Exception as e:
        print(f"PostgreSQL Diagnostic Error: {e}")
        print("\nFALLBACK: Checking SQLite...")
        import sqlite3
        try:
            conn = sqlite3.connect('backend/bqs.db')
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            print("SQLite Tables:", cur.fetchall())
            conn.close()
        except Exception as e2:
            print(f"SQLite Check Error: {e2}")

if __name__ == "__main__":
    diagnostic()
