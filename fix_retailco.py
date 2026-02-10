
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser, OppScoreVersion

def fix_retailco():
    db = SessionLocal()
    try:
        opp = db.query(Opportunity).filter(Opportunity.opp_name.like('%RetailCo%')).first()
        if not opp:
            print("RetailCo NOT FOUND")
            return

        print(f"Fixing: {opp.opp_id} | {opp.opp_name}")
        
        # 1. Assign Practice Head if missing
        if not opp.assigned_practice_head_id:
            # Assign Sarah Mitchell (ph-001)
            opp.assigned_practice_head_id = 'ph-001'
            print("Assigned Sarah Mitchell (PH) to RetailCo.")

        # 2. Check if SP has submitted
        sp_sub = db.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp.opp_id,
            OppScoreVersion.status == 'SUBMITTED'
        ).all()
        
        print(f"Submitted versions found: {len(sp_sub)}")
        
        # 3. Force status update using the new logic (just doing it directly here)
        # If there's no SA assigned, or if SA is also done, move to READY_FOR_REVIEW
        sa_ready = True
        if opp.assigned_sa_id:
             sa_ver = db.query(OppScoreVersion).filter(
                OppScoreVersion.opp_id == opp.opp_id,
                OppScoreVersion.created_by_user_id == opp.assigned_sa_id,
                OppScoreVersion.status == "SUBMITTED"
            ).first()
             sa_ready = (sa_ver is not None)
        
        if len(sp_sub) > 0 and sa_ready:
            opp.workflow_status = "READY_FOR_REVIEW"
            opp.combined_submission_ready = True
            print("Updated workflow status to READY_FOR_REVIEW.")
        else:
            print(f"Status remains: {opp.workflow_status} (Waiting for SA: {opp.assigned_sa_id})")

        db.commit()
        print("✅ RetailCo Fixed!")

    finally:
        db.close()

if __name__ == "__main__":
    fix_retailco()
