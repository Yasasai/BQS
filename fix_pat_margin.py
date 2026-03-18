import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_schema():
    if not DATABASE_URL:
        print("DATABASE_URL not found in environment.")
        return

    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            print("Executing ALTER TABLE command...")
            connection.execute(text("ALTER TABLE opportunity ADD COLUMN pat_margin FLOAT;"))
            transaction.commit()
            print("Successfully added column 'pat_margin' to 'opportunity' table.")
        except Exception as e:
            transaction.rollback()
            # Catch DuplicateColumn error or similar
            if "already exists" in str(e).lower():
                print("Column 'pat_margin' already exists. Skipping.")
            else:
                print(f"An error occurred: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    fix_schema()
