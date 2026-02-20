
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import or_

def investigate_sarah():
    db = SessionLocal()
    try:
        # 1. Find User by Name "Sarah"
        sarah = db.query(AppUser).filter(AppUser.display_name.ilike('%Sarah%')).first()
        if not sarah:
            print("User 'Sarah' not found.")
            # List some PHs
            phs = db.query(AppUser).filter(AppUser.role == 'PH').limit(5).all()
            print("Available PHs:", [f"{u.display_name} ({u.role})" for u in phs])
            return

        print(f"Found User: {sarah.display_name} | ID: {sarah.user_id} | Role: {sarah.role}")
        
        # 2. Find Opportunities assigned to Sarah
        opps = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == sarah.user_id).all()
        print(f"Total Opportunities Assigned to Sarah: {len(opps)}")
        
        # 3. Analyze why they might be hidden from 'Action Required'
        # Filter Logic: assigned_sa_id IS NULL AND workflow_status IN [...]
        
        allowed_statuses = ['NEW', 'OPEN', 'HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', None, '']
        print(f"Action Required Allowed Statuses: {allowed_statuses}")
        
        hidden_count = 0
        visible_count = 0
        
        for opp in opps:
            is_sa_unassigned = (opp.assigned_sa_id is None)
            is_status_allowed = (opp.workflow_status in allowed_statuses)
            
            if is_sa_unassigned and is_status_allowed:
                visible_count += 1
                # print(f" [VISIBLE] {opp.opp_id} | Status: {opp.workflow_status}")
            else:
                hidden_count += 1
                print(f" [HIDDEN]  {opp.opp_id} | Status: {opp.workflow_status} | SA: {opp.assigned_sa_id}")
                if not is_sa_unassigned:
                    print(f"    -> Reason: SA is already assigned ({opp.assigned_sa_id})")
                if not is_status_allowed:
                    print(f"    -> Reason: Status '{opp.workflow_status}' not in allowed list")

        print(f"Summary: Visible={visible_count}, Hidden={hidden_count}")

    finally:
        db.close()

if __name__ == "__main__":
    investigate_sarah()
