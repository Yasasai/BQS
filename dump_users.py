import sqlite3
conn = sqlite3.connect('backend/bqs.db')
c = conn.cursor()
c.execute("SELECT user_id, display_name, role FROM users")
rows = c.fetchall()
with open('users_dump.txt', 'w') as f:
    for r in rows:
        f.write(f"{r}\n")
conn.close()
