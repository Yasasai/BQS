from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/bqs"
engine = create_engine(DATABASE_URL)

def verify():
    with engine.connect() as conn:
        print("Checking app_user table...")
        res = conn.execute(text("SELECT count(*) FROM app_user")).fetchone()
        print(f"Total users: {res[0]}")
        
        print("\nSample Users with new metadata:")
        res = conn.execute(text("""
            SELECT email, display_name, manager_email, corporate_title, geo_region, practice_name 
            FROM app_user 
            WHERE manager_email IS NOT NULL OR corporate_title IS NOT NULL OR geo_region IS NOT NULL OR practice_name IS NOT NULL
            LIMIT 10
        """)).fetchall()
        for r in res:
            print(f"Email: {r[0]}, Name: {r[1]}, Manager: {r[2]}, Title: {r[3]}, Geo: {r[4]}, Practice: {r[5]}")
            
        print("\nChecking Role Assignments:")
        res = conn.execute(text("""
            SELECT r.role_code, count(*) 
            FROM user_role ur 
            JOIN role r ON ur.role_id = r.role_id 
            GROUP BY r.role_code
        """)).fetchall()
        for r in res:
            print(f"Role: {r[0]}, Count: {r[1]}")

if __name__ == "__main__":
    verify()
