import sys
sys.path.append('c:/Users/YasasviUpadrasta/Documents/Data Analytics/Internal Innovation/BQS')

from backend.app.core.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        # Add workflow_status column
        conn.execute(text("""
            ALTER TABLE opportunity 
            ADD COLUMN IF NOT EXISTS workflow_status VARCHAR(50);
        """))
        
        # Add assigned_sa column
        conn.execute(text("""
            ALTER TABLE opportunity 
            ADD COLUMN IF NOT EXISTS assigned_sa VARCHAR(255);
        """))
        
        # Set default workflow_status for existing records
        conn.execute(text("""
            UPDATE opportunity 
            SET workflow_status = 'NEW' 
            WHERE workflow_status IS NULL;
        """))
        
        conn.commit()
        print("✅ Migration successful!")
        print("   - Added workflow_status column")
        print("   - Added assigned_sa column")
        print("   - Set default status to 'NEW' for existing records")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
