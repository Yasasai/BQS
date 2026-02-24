import os
from dotenv import load_dotenv

load_dotenv()

print("Checking environment variables...")
print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
print(f"DB_PORT: {os.getenv('DB_PORT', '5432')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'bqs')}")
print(f"DB_USER: {os.getenv('DB_USER', 'postgres')}")
print(f"DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'NOT SET'}")

print("\nTrying to connect to database...")
try:
    from backend.app.core.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Check if columns exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'opportunity' 
            AND column_name IN ('workflow_status', 'assigned_sa')
        """))
        existing_cols = [row[0] for row in result]
        print(f"\nExisting workflow columns: {existing_cols}")
        
        if 'workflow_status' not in existing_cols:
            print("\n⚠️  workflow_status column is missing - migration needed")
        if 'assigned_sa' not in existing_cols:
            print("⚠️  assigned_sa column is missing - migration needed")
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
