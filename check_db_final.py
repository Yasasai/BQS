
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
insp = inspect(engine)

print(f"Tables found: {insp.get_table_names()}")
if insp.has_table('opp_score_section_values'):
    cols = [c['name'] for c in insp.get_columns('opp_score_section_values')]
    print(f"Columns in opp_score_section_values: {cols}")
else:
    print("Table 'opp_score_section_values' NOT FOUND")

if insp.has_table('opp_score_section'):
    rows = engine.connect().execute("SELECT section_code FROM opp_score_section").fetchall()
    print(f"Sections in DB: {[r[0] for r in rows]}")
