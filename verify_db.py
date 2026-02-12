
import sys

print("Starting verification script...")

try:
    with open("verification_result.txt", "w") as f:
        f.write("STARTING\n")
        try:
            import psycopg2
            f.write("Imported psycopg2.\n")
        except ImportError as e:
            f.write(f"ImportError: {e}\n")
            sys.exit(1)

        DB_CONFIG = {
            "dbname": "bqs",
            "user": "postgres",
            "password": "Abcd1234",
            "host": "127.0.0.1",
            "port": "5432"
        }

        f.write("Connecting...\n")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            f.write("Querying...\n")
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='opp_score_version' AND column_name IN ('sa_submitted', 'sp_submitted')")
            columns = [row[0] for row in cur.fetchall()]
            
            if 'sa_submitted' in columns and 'sp_submitted' in columns:
                f.write("PASS: Both columns exist.\n")
            else:
                f.write(f"FAIL: Found {columns}\n")
                
            cur.close()
            conn.close()
            f.write("DONE\n")
        except Exception as e:
            f.write(f"DB Error: {e}\n")

except Exception as e:
    print(f"File writing error: {e}")

print("Verification finished.")
