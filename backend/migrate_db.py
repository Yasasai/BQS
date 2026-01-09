from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Add win_probability column
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN win_probability FLOAT;"))
            print("Added win_probability column.")
        except Exception as e:
            print(f"Error adding win_probability (might already exist): {e}")
            
        try:
             # Ensure currency column exists (it was in the file but maybe not in DB if created earlier)
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN currency VARCHAR;"))
            print("Added currency column.")
        except Exception as e:
             # Ignore if exists
             pass
             
        conn.commit()

if __name__ == "__main__":
    migrate()
