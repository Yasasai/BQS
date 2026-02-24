
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, Role, UserRole

def seed_final():
    db = SessionLocal()
    try:
        # 1. Ensure Roles
        roles = {
            'GH': 'Global Head',
            'PH': 'Practice Head',
            'SH': 'Sales Head',
            'SA': 'Solution Architect',
            'SP': 'Salesperson'
        }
        for code, name in roles.items():
            r = db.query(Role).filter(Role.role_code == code).first()
            if not r:
                db.add(Role(role_code=code, role_name=name))
        db.commit()

        # 2. Ensure Emily White (SP)
        emily = db.query(AppUser).filter(AppUser.user_id == 'sp-001').first()
        if not emily:
            emily = AppUser(user_id='sp-001', email='emily.white@company.com', display_name='Emily White', is_active=True)
            db.add(emily)
            db.flush()
        
        sp_role = db.query(Role).filter(Role.role_code == 'SP').first()
        ur = db.query(UserRole).filter_by(user_id=emily.user_id, role_id=sp_role.role_id).first()
        if not ur:
            db.add(UserRole(user_id=emily.user_id, role_id=sp_role.role_id))
        db.commit()

        # 3. Ensure Robert Chen (SH)
        robert = db.query(AppUser).filter(AppUser.user_id == 'sh-001').first()
        if not robert:
            robert = AppUser(user_id='sh-001', email='robert.chen@company.com', display_name='Robert Chen', is_active=True)
            db.add(robert)
            db.flush()
        
        sh_role = db.query(Role).filter(Role.role_code == 'SH').first()
        ur = db.query(UserRole).filter_by(user_id=robert.user_id, role_id=sh_role.role_id).first()
        if not ur:
            db.add(UserRole(user_id=robert.user_id, role_id=sh_role.role_id))
        db.commit()

        # 4. Prepare Opportunities for SH
        # Grab first 10 active ones
        opps = db.query(Opportunity).filter(Opportunity.is_active == True).limit(10).all()
        print(f"Assigning {len(opps)} opportunities to Robert (SH)...")
        for o in opps:
            o.assigned_sales_head_id = 'sh-001'
            o.assigned_sp_id = None # Clear assignment to make button visible
            # Set to NEW/PH_ASSIGNED so it stays in Action Required
            if not o.workflow_status or o.workflow_status in ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']:
                o.workflow_status = 'NEW'
            o.sh_approval_status = 'PENDING'
            
        db.commit()
        print("✅ Final Seed Complete!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_final()
