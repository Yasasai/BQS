
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

def run_migration():
    engine = create_engine(DATABASE_URL)
    
    commands = [
        "ALTER TABLE opportunity ADD COLUMN IF NOT EXISTS assigned_finance_id VARCHAR;",
        "ALTER TABLE opportunity ADD COLUMN IF NOT EXISTS assigned_legal_id VARCHAR;"
    ]
    
    print(f"Connecting to: {DATABASE_URL.split('@')[-1]}") # Log host/port without password
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                # Use text() for raw SQL in SQLAlchemy 2.0+
                conn.execute(text(cmd))
                conn.commit()
                print(f"✅ Executed: {cmd}")
            except Exception as e:
                print(f"⚠️ Error executing '{cmd}': {e}")

if __name__ == "__main__":
    run_migration()
    print("🚀 Migration script finished.")
