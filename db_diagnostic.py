
from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
insp = inspect(engine)

print("--- TABLES ---")
tables = insp.get_table_names()
for t in tables:
    print(f"\nTable: {t}")
    cols = insp.get_columns(t)
    for c in cols:
        print(f"  - {c['name']} ({c['type']})")
