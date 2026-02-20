
import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)

def dump():
    print("--- DATABASE DUMP ---")
    with engine.connect() as conn:
        # Tables
        tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
        print(f"Tables found: {[t[0] for t in tables]}")
        
        for t in [t[0] for t in tables]:
            print(f"\n--- Table: {t} ---")
            try:
                # Columns
                cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{t}'")).fetchall()
                print(f"Columns: {[(c[0], c[1]) for c in cols]}")
                
                # Row count
                count = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                print(f"Count: {count}")
                
                if count > 0 and t in ['opp_score_section', 'app_user']:
                    rows = conn.execute(text(f"SELECT * FROM {t} LIMIT 5")).fetchall()
                    print(f"Sample data: {rows}")
            except Exception as e:
                print(f"Error reading {t}: {e}")

if __name__ == "__main__":
    dump()
