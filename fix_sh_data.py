
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, Role, UserRole

def fix_sh_data():
    db = SessionLocal()
    try:
        # 1. Ensure Robert Chen exists as SH
        sh_id = 'sh-001'
        robert = db.query(AppUser).filter(AppUser.user_id == sh_id).first()
        if not robert:
            print("Creating Robert Chen (SH)...")
            robert = AppUser(user_id=sh_id, email='robert.chen@company.com', display_name='Robert Chen')
            db.add(robert)
            db.flush()
            
        sh_role = db.query(Role).filter(Role.role_code == 'SH').first()
        if sh_role:
            ur = db.query(UserRole).filter_by(user_id=sh_id, role_id=sh_role.role_id).first()
            if not ur:
                db.add(UserRole(user_id=sh_id, role_id=sh_role.role_id))

        # 2. Ensure Emily White exists as SP
        sp_id = 'sp-001'
        emily = db.query(AppUser).filter(AppUser.user_id == sp_id).first()
        if not emily:
            print("Creating Emily White (SP)...")
            emily = AppUser(user_id=sp_id, email='emily.white@company.com', display_name='Emily White')
            db.add(emily)
            db.flush()
            
        sp_role = db.query(Role).filter(Role.role_code == 'SP').first()
        if sp_role:
            ur = db.query(UserRole).filter_by(user_id=sp_id, role_id=sp_role.role_id).first()
            if not ur:
                db.add(UserRole(user_id=sp_id, role_id=sp_role.role_id))

        # 3. Assign 10 opportunities to Robert as SH
        # Grab some opps that Sarah (PH) has, to simulate shared deals
        sarah_opps = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-001').limit(10).all()
        
        print(f"Assigning SH 'sh-001' to {len(sarah_opps)} opportunities...")
        for opp in sarah_opps:
            opp.assigned_sales_head_id = sh_id
            # Also reset SP to None to ensure they appear in "Action Required"
            opp.assigned_sp_id = None
            
        db.commit()
        print("✅ Success! Sales Head data ready.")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_sh_data()
