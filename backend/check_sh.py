
import sys
import os
print("Started check_sh.py")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Role, UserRole

def check_sh():
    db = SessionLocal()
    try:
        print("🔍 checking SH role...")
        sh_role = db.query(Role).filter(Role.role_code == 'SH').first()
        if not sh_role:
            print("❌ SH Role not found!")
            return

        users = db.query(AppUser).join(UserRole).filter(UserRole.role_id == sh_role.role_id).all()
        print(f"✅ Found {len(users)} SH users:")
        for u in users:
            print(f"   - {u.display_name} ({u.email}) [ID: {u.user_id}]")

        # Check Kunal specifically
        kunal = db.query(AppUser).filter(AppUser.display_name.like("%Kunal%")).first()
        if kunal:
            print(f"\n👤 Kunal Info: {kunal.display_name} ({kunal.user_id})")
            k_roles = db.query(Role).join(UserRole).filter(UserRole.user_id == kunal.user_id).all()
            print(f"   Roles: {[r.role_code for r in k_roles]}")
        else:
            print("\n❌ Kunal not found in AppUser!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_sh()
