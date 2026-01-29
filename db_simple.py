
import sys
import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
print("Connecting...")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Connected.")
        res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in res]
        print(f"Tables: {tables}")
except Exception as e:
    print(f"Error: {e}")
