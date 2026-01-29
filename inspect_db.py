
import os
import sys
from sqlalchemy import create_engine, text

# Adjust path to find backend modules
sys.path.append(os.getcwd())

# Configuration
DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"

def check_tables():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- Table Row Counts ---")
        tables = [
            "opportunities", "opportunity", "oracle_opportunities", "global_open_opportunities",
            "app_user", "role", "user_role", 
            "opp_score_version", "opp_score_section", "opp_score_section_value",
            "opportunity_assignment", "practice"
        ]
        
        real_tables = []
        for t in tables:
            try:
                result = conn.execute(text(f"SELECT count(*) FROM {t}"))
                count = result.scalar()
                print(f"✅ {t}: {count}")
                real_tables.append(t)
            except Exception as e:
                print(f"❌ {t}: (Does not exist)")
                
        return real_tables

if __name__ == "__main__":
    check_tables()
