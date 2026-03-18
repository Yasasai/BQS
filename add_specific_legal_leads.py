import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Path bootstrap
this_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(this_dir, "backend", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

USERS_TO_ADD = [
    {"id": "21", "email": "legal1@company.com", "name": "Amit Sharma - Legal"},
    {"id": "22", "email": "legal2@company.com", "name": "Priya Menon - Legal"},
    {"id": "23", "email": "legal3@company.com", "name": "Rohit Gupta - Legal"}
]

def add_legal_users():
    with engine.connect() as conn:
        # 1. Ensure LEGAL role exists (id: 6 as per seed_users.py)
        conn.execute(text("""
            INSERT INTO role (role_id, role_code, role_name)
            VALUES (6, 'LEGAL', 'Legal Head')
            ON CONFLICT (role_code) DO UPDATE SET role_name = 'Legal Head';
        """))
        
        # 2. Add Users
        for user in USERS_TO_ADD:
            print(f"Processing {user['name']}...")
            conn.execute(text("""
                INSERT INTO app_user (user_id, email, display_name, is_active, created_at)
                VALUES (:id, :email, :name, true, NOW())
                ON CONFLICT (email) DO UPDATE SET 
                    display_name = :name,
                    is_active = true;
            """), {"id": user['id'], "email": user['email'], "name": user['name']})
            
            # 3. Map to Role
            conn.execute(text("""
                INSERT INTO user_role (user_id, role_id)
                SELECT :id, role_id FROM role WHERE role_code = 'LEGAL'
                ON CONFLICT (user_id, role_id) DO NOTHING;
            """), {"id": user['id']})
        
        conn.commit()
    print("Successfully added/updated legal lead users.")

if __name__ == "__main__":
    add_legal_users()
