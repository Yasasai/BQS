
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "bqs",
    "user": "postgres",
    "password": "Abcd1234",
    "host": "127.0.0.1",
    "port": "5432"
}

def heal_database():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Checking for missing columns in opp_score_version...")
        
        # Check sa_submitted
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='opp_score_version' AND column_name='sa_submitted'")
        if not cur.fetchone():
            print("Adding sa_submitted column...")
            cur.execute("ALTER TABLE opp_score_version ADD COLUMN sa_submitted BOOLEAN DEFAULT FALSE")
        else:
            print("Column sa_submitted already exists.")
            
        # Check sp_submitted
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='opp_score_version' AND column_name='sp_submitted'")
        if not cur.fetchone():
            print("Adding sp_submitted column...")
            cur.execute("ALTER TABLE opp_score_version ADD COLUMN sp_submitted BOOLEAN DEFAULT FALSE")
        else:
            print("Column sp_submitted already exists.")
            
        cur.close()
        conn.close()
        print("Database healing complete.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    heal_database()
