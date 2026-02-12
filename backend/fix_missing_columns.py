
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_columns():
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
        
        columns_to_add = [
            ("assigned_practice_head_id", "VARCHAR"),
            ("assigned_sales_head_id", "VARCHAR"),
            ("assigned_sa_id", "VARCHAR"),
            ("assigned_sp_id", "VARCHAR"),
            ("gh_approval_status", "VARCHAR DEFAULT 'PENDING'"),
            ("ph_approval_status", "VARCHAR DEFAULT 'PENDING'"),
            ("sh_approval_status", "VARCHAR DEFAULT 'PENDING'"),
            ("combined_submission_ready", "BOOLEAN DEFAULT FALSE")
        ]
        
        with conn.cursor() as cur:
            for col_name, col_type in columns_to_add:
                # Check if column exists
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='opportunity' AND column_name=%s;
                """, (col_name,))
                
                if cur.fetchone():
                    print(f"✅ Column '{col_name}' already exists.")
                else:
                    print(f"🛠️ Adding '{col_name}' column...")
                    query = f"ALTER TABLE opportunity ADD COLUMN {col_name} {col_type};"
                    print(f"Executing: {query}")
                    cur.execute(query)
                    print(f"✅ Successfully added '{col_name}'.")
                
        conn.close()
        print("\n🎉 Schema fixed successfully!")
    except Exception as e:
        print(f"❌ Error fixing columns: {e}")

if __name__ == "__main__":
    fix_columns()
