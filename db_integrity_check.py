
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, UserRole, Role

def check_db_integrity():
    db = SessionLocal()
    try:
        print("--- APP USERS ---")
        users = db.query(AppUser).all()
        for u in users:
            roles = [r.role.role_code for r in u.user_roles]
            print(f"ID: {u.user_id} | Name: {u.display_name} | Roles: {roles}")
            
        print("\n--- OPPORTUNITIES PH ASSIGNMENTS ---")
        assigned_ph_ids = db.query(Opportunity.assigned_practice_head_id).filter(Opportunity.assigned_practice_head_id.isnot(None)).distinct().all()
        ph_ids = [r[0] for r in assigned_ph_ids]
        print(f"PH IDs found in assignments: {ph_ids}")
        
        for pid in ph_ids:
            exists = db.query(AppUser).filter(AppUser.user_id == pid).first()
            if not exists:
                print(f"⚠️  WARNING: Opportunity points to PH ID '{pid}' but THIS USER DOES NOT EXIST in app_user table.")
            else:
                print(f"✅ PH ID '{pid}' exists in app_user table.")

    finally:
        db.close()

if __name__ == "__main__":
    check_db_integrity()
