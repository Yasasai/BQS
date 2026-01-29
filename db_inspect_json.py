
import os
import json
from sqlalchemy import create_engine, inspect

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
insp = inspect(engine)

data = {}
for table in insp.get_table_names():
    cols = insp.get_columns(table)
    data[table] = [c['name'] for c in cols]

with open('db_schema.json', 'w') as f:
    json.dump(data, f, indent=4)
print("Done.")
