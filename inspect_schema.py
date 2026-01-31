
import os
import sys
from sqlalchemy import create_engine, text

# Adjust path to find backend modules
sys.path.append(os.getcwd())

# Configuration
DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"

def inspect_columns():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- Inspecting opp_score_section_value columns ---")
        try:
            # Query information_schema
            query = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'opp_score_section_value'
            """)
            result = conn.execute(query).fetchall()
            
            found_cols = {row[0]: row[1] for row in result}
            
            expected_cols = ["score_value_id", "score_version_id", "section_code", "score", "notes", "selected_reasons"]
            
            for col in expected_cols:
                if col in found_cols:
                    print(f"✅ {col}: {found_cols[col]}")
                else:
                    print(f"❌ {col}: MISSING")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    inspect_columns()
