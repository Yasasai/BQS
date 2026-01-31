import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import DATABASE_URL

def check_users():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("\n--- Users Check ---")
        result = conn.execute(text("SELECT email, display_name FROM app_user"))
        users = result.fetchall()
        if not users:
            print("No users found.")
        else:
            for u in users:
                print(f"User: {u.display_name} ({u.email})")
                
        print("\n--- Roles Check ---")
        roles = conn.execute(text("SELECT role_code, role_name FROM role"))
        for r in roles:
            print(f"Role: {r.role_code} - {r.role_name}")

        print("\n--- User Roles ---")
        ur = conn.execute(text("SELECT u.email, r.role_code FROM app_user u JOIN user_role ur ON u.user_id = ur.user_id JOIN role r ON ur.role_id = r.role_id"))
        for row in ur:
            print(f"{row.email} has role {row.role_code}")

if __name__ == "__main__":
    check_users()
