import os
import psycopg2
from dotenv import load_dotenv

# Load env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'bqs'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Abcd1234'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

def check_sync_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Checking sync_meta table...")
        cursor.execute("SELECT * FROM sync_meta")
        rows = cursor.fetchall()
        
        if rows:
            print(f"✓ Found {len(rows)} records in sync_meta:")
            for row in rows:
                print(f"  - Key: {row[1]}, Last Sync: {row[2]}, Updated: {row[4]}")
        else:
            print("⚠ Table exists but is empty.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == "__main__":
    check_sync_status()
