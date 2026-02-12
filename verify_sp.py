
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Role, UserRole

def verify_sp_users():
    db = SessionLocal()
    try:
        sp_role = db.query(Role).filter(Role.role_code == 'SP').first()
        if not sp_role:
            print("❌ Role 'SP' does not exist in DB!")
            return
            
        users = db.query(AppUser).join(UserRole).filter(UserRole.role_id == sp_role.role_id).all()
        print(f"📊 Found {len(users)} users with role 'SP':")
        for u in users:
            print(f"  - ID: {u.user_id} | Name: {u.display_name} | Email: {u.email}")
            
        if len(users) == 0:
            print("⚠️ No Salespersons (SP) found. This is why the dropdown is likely empty.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_sp_users()
