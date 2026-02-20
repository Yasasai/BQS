
import sys
import os
print("Started check_sp.py")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Role, UserRole

def check_sp():
    db = SessionLocal()
    try:
        print("🔍 checking SP role...")
        sp_role = db.query(Role).filter(Role.role_code == 'SP').first()
        if not sp_role:
            print("❌ SP Role not found!")
            return

        users = db.query(AppUser).join(UserRole).filter(UserRole.role_id == sp_role.role_id).all()
        print(f"✅ Found {len(users)} SP users:")
        for u in users:
            print(f"   - {u.display_name} ({u.email}) [ID: {u.user_id}]")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_sp()
