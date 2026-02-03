
import os
import sys
from sqlalchemy import create_engine, text
from backend.app.core.database import DATABASE_URL

def inspect_sync_meta():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("--- Checking sync_meta columns ---")
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'sync_meta'"))
            columns = result.fetchall()
            if not columns:
                print("Table 'sync_meta' NOT FOUND in information_schema")
            else:
                for col in columns:
                    print(f"Column: {col[0]}, Type: {col[1]}")
            
            print("\n--- Checking actual rows (limit 1) ---")
            try:
                rows = conn.execute(text("SELECT * FROM sync_meta LIMIT 1")).fetchall()
                print(f"Row count in sample: {len(rows)}")
                if rows:
                    print(f"Sample row: {rows[0]}")
            except Exception as e:
                print(f"Error querying table: {e}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    inspect_sync_meta()
