import psycopg2
import sys

try:
    conn = psycopg2.connect('postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs', connect_timeout=5)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM opportunities')
    count = cur.fetchone()[0]
    print(f'COUNT={count}')
    conn.close()
except Exception as e:
    print(f'ERROR={e}')
