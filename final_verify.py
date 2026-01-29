
import os
import sys
import json
from sqlalchemy import create_engine, inspect, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
insp = inspect(engine)

def verify():
    print("--- 🔍 FINAL SCHEMA VERIFICATION 🔍 ---")
    
    expected_tables = ["opportunity", "opp_score_version", "opp_score_values", "opp_score_section"]
    actual_tables = insp.get_table_names()
    
    for t in expected_tables:
        if t in actual_tables:
            print(f"✅ Table '{t}' EXISTS.")
            cols = [c['name'] for c in insp.get_columns(t)]
            print(f"   Columns: {cols}")
            
            with engine.connect() as conn:
                count = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                print(f"   Row Count: {count}")
        else:
            print(f"❌ Table '{t}' is MISSING from {actual_tables}")

    # Check for the old table to ensure it's gone
    if "opp_score_section_values" in actual_tables:
        print("⚠️ Warning: Old table 'opp_score_section_values' still exists.")
    else:
        print("✅ Old table 'opp_score_section_values' has been REMOVED.")

if __name__ == "__main__":
    verify()
