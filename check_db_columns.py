
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def check_columns():
    engine = create_engine(DATABASE_URL)
    insp = inspect(engine)
    columns = insp.get_columns("opportunity")
    print("Columns in 'opportunity' table:")
    for col in columns:
        print(f" - {col['name']} ({col['type']})")

if __name__ == "__main__":
    check_columns()
