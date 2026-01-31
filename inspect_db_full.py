
from sqlalchemy import create_engine, inspect, text
import os

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)

def inspect_db():
    insp = inspect(engine)
    for table_name in insp.get_table_names():
        print(f"\nTable: {table_name}")
        for column in insp.get_columns(table_name):
            print(f"  - {column['name']}: {column['type']}")

if __name__ == "__main__":
    inspect_db()
