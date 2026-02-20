
import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)

def check():
    with engine.connect() as conn:
        for table in ["opp_score_section", "opp_score_version", "opp_score_section_values"]:
            try:
                res = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                print(f"Table {table}: {res} rows")
            except Exception as e:
                print(f"Table {table}: ERROR - {e}")

if __name__ == "__main__":
    check()
