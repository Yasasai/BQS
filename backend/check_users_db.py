
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, UserRole, Role

def check_users():
    db = SessionLocal()
    try:
        print("--- Checking Roles ---")
        roles = db.query(Role).all()
        for r in roles:
            print(f"Role: {r.role_code} (ID: {r.role_id})")

        print("\n--- Checking Users & Assignments ---")
        users = db.query(AppUser).all()
        for u in users:
            user_roles = db.query(UserRole).filter(UserRole.user_id == u.user_id).all()
            role_codes = []
            for ur in user_roles:
                role = db.query(Role).filter(Role.role_id == ur.role_id).first()
                if role:
                    role_codes.append(role.role_code)
            
            print(f"User: {u.display_name} ({u.email}) - Roles: {role_codes}")

    finally:
        db.close()

if __name__ == "__main__":
    check_users()
