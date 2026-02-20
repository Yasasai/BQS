
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print("🚀 Script starting...")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"📂 Path added: {sys.path[-1]}")


from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Role, UserRole

def check_kunal():
    db = SessionLocal()
    try:
        print("🔍 Searching for Kunal...")
        kunal = db.query(AppUser).filter(AppUser.display_name.like("%Kunal%")).first()
        if not kunal:
            print("❌ Kunal not found in AppUser table!")
        else:
            print(f"✅ Found Kunal:")
            print(f"   ID: {kunal.user_id}")
            print(f"   Name: {kunal.display_name}")
            print(f"   Email: {kunal.email}")
            
            roles = db.query(Role).join(UserRole).filter(UserRole.user_id == kunal.user_id).all()
            print(f"   Roles: {[r.role_code for r in roles]}")
            
            # Check if he shows up in SH query
            sh_role = db.query(Role).filter(Role.role_code == 'SH').first()
            if sh_role:
                is_sh = db.query(UserRole).filter(UserRole.user_id == kunal.user_id, UserRole.role_id == sh_role.role_id).first()
                print(f"   Is Assigned SH Role? {'Yes' if is_sh else 'No'}")

    finally:
        db.close()

if __name__ == "__main__":
    check_kunal()
