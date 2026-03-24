
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, Role, UserRole

def assign_sa_work():
    db = SessionLocal()
    try:
        # 1. Ensure SA John Doe exists
        john = db.query(AppUser).filter(AppUser.user_id == 'sa-001').first()
        if not john:
            print("Creating John Doe (SA)...")
            john = AppUser(user_id='sa-001', email='john.doe@company.com', display_name='John Doe')
            db.add(john)
        
        # 2. Get 5 opportunities assigned to Sarah (ph-001)
        # We'll assign John Doe as the SA for these
        sarah_opps = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id == 'ph-001'
        ).limit(5).all()
        
        print(f"Assigning SA 'sa-001' to {len(sarah_opps)} of Sarah's opportunities...")
        for opp in sarah_opps:
            opp.assigned_sa_id = 'sa-001'
            # Status doesn't strictly matter now because of inclusive filter, 
            # but let's set it to something logical.
            opp.workflow_status = 'HEADS_ASSIGNED' 

        db.commit()
        print("✅ Success! 5 opportunities assigned to SA John Doe.")
        
    finally:
        db.close()

if __name__ == "__main__":
    assign_sa_work()
