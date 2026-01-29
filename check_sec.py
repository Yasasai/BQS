
import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)

def check_sections():
    print("Checking sections...")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT section_code FROM opp_score_section")).fetchall()
        print(f"DATABASE SECTIONS: {[r[0] for r in res]}")

if __name__ == "__main__":
    check_sections()
