"""
Add workflow_status and assigned_sa columns to opportunity table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bqs")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def migrate():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    try:
        # Add workflow_status column
        cursor.execute("""
            ALTER TABLE opportunity 
            ADD COLUMN IF NOT EXISTS workflow_status VARCHAR(50);
        """)
        
        # Add assigned_sa column
        cursor.execute("""
            ALTER TABLE opportunity 
            ADD COLUMN IF NOT EXISTS assigned_sa VARCHAR(255);
        """)
        
        # Set default workflow_status for existing records
        cursor.execute("""
            UPDATE opportunity 
            SET workflow_status = 'NEW' 
            WHERE workflow_status IS NULL;
        """)
        
        conn.commit()
        print("✅ Migration successful: Added workflow_status and assigned_sa columns")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
