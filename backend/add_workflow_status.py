
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def add_column():
    try:
        print(f"Connecting to database bqs as user postgres...")
        conn = psycopg2.connect(
            dbname='bqs', 
            user='postgres', 
            host='127.0.0.1', 
            password='Abcd1234', 
            port=5432,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            # Check if column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='opportunity' AND column_name='workflow_status';
            """)
            
            if cur.fetchone():
                print("✅ Column 'workflow_status' already exists in 'opportunity' table.")
            else:
                print("🛠️ Adding 'workflow_status' column to 'opportunity' table...")
                cur.execute("ALTER TABLE opportunity ADD COLUMN workflow_status VARCHAR;")
                print("✅ Successfully added 'workflow_status' column.")
                
        conn.close()
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_column()
