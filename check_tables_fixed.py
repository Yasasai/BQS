
from sqlalchemy import create_engine, text
from backend.app.core.database import DATABASE_URL

def check():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Checking sync_meta...", end=" ")
        try:
            conn.execute(text("SELECT meta_key FROM sync_meta LIMIT 1"))
            print("✅ OK")
        except Exception as e:
            print(f"❌ FAIL: {e}")
            
        print("Checking sync_state...", end=" ")
        try:
            conn.execute(text("SELECT id FROM sync_state LIMIT 1"))
            print("✅ OK")
        except Exception as e:
            print(f"❌ FAIL: {e}")

if __name__ == "__main__":
    check()
