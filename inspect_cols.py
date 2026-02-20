
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
insp = inspect(engine)

for table in ["opportunity", "opp_score_version", "opp_score_section_values"]:
    print(f"\nTable: {table}")
    if insp.has_table(table):
        cols = insp.get_columns(table)
        for c in cols:
            print(f"  - {c['name']} ({c['type']})")
    else:
        print("  !!! MISSING !!!")
