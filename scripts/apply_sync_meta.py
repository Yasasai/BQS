import os
import psycopg2
from dotenv import load_dotenv

# Load env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# DB Config
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'bqs'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Abcd1234'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

def apply_migration():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        migration_file = os.path.join(base_dir, 'backend', 'migrations', 'sync_meta.sql')
        with open(migration_file, 'r') as f:
            sql = f.read()
            
        print(f"Applying migration from {migration_file}...")
        cursor.execute(sql)
        conn.commit()
        print("✓ Migration applied successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    apply_migration()
