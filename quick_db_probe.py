import psycopg2
import sys

try:
    conn = psycopg2.connect("postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")
    cur = conn.cursor()
    print("✅ Connected to database.")
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [t[0] for t in cur.fetchall()]
    print(f"Tables: {tables}")
    
    if 'opportunity_details' in tables:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'opportunity_details'")
        cols = [c[0] for c in cur.fetchall()]
        print(f"Columns in opportunity_details: {cols}")
        
        cur.execute("SELECT count(*) FROM opportunity_details")
        count = cur.fetchone()[0]
        print(f"Total records: {count}")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
