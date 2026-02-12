import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM opportunities")
    print(f"Connection Successful! Total Opps: {cur.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"FAILED TO CONNECT: {e}")
