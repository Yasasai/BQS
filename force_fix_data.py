
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, Role, UserRole

def fix_and_assign():
    db = SessionLocal()
    try:
        # 1. Ensure Sarah exists with correct ID
        sarah = db.query(AppUser).filter(AppUser.user_id == 'ph-001').first()
        if not sarah:
            print("Creating Sarah...")
            sarah = AppUser(user_id='ph-001', email='sarah.mitchell@company.com', display_name='Sarah Mitchell')
            db.add(sarah)
        
        # 2. Ensure Role PH exists
        ph_role = db.query(Role).filter(Role.role_code == 'PH').first()
        if not ph_role:
            ph_role = Role(role_id=2, role_code='PH', role_name='Practice Head')
            db.add(ph_role)
            db.flush()
            
        # 3. Assign Sarah to PH Role
        user_role = db.query(UserRole).filter_by(user_id='ph-001', role_id=ph_role.role_id).first()
        if not user_role:
            db.add(UserRole(user_id='ph-001', role_id=ph_role.role_id))

        # 4. CRITICAL: Find opportunities that are "NEW/OPEN" and assign them to Sarah
        # This simulates real data that she should see in 'Action Required'
        new_opps = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            # Assign any opp that is not already assigned to another PH, or just grab first 10
            Opportunity.assigned_practice_head_id.is_(None)
        ).limit(10).all()
        
        print(f"Assigning {len(new_opps)} opportunities to Sarah (ph-001)...")
        for opp in new_opps:
            opp.assigned_practice_head_id = 'ph-001'
            # Reset status to something that falls into 'Action Required' for PH
            # Based on current waterfall: not completed, not review, SA is None
            opp.workflow_status = 'NEW'
            opp.ph_approval_status = 'PENDING'
            opp.assigned_sa_id = None
            
        db.commit()
        print("✅ Success! 10 opportunities assigned to Sarah.")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_and_assign()
