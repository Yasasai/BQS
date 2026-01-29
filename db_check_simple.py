
import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cur.fetchall()
        print(f"TABLES: {tables}")
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
