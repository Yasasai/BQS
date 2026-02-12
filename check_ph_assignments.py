
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import func

def check_ph_assignments():
    db = SessionLocal()
    try:
        # Find all opportunities where PH is assigned but SA is NOT assigned
        ph_assigned_no_sa = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id.isnot(None),
            Opportunity.assigned_sa_id.is_(None)
        ).all()
        
        print(f"Found {len(ph_assigned_no_sa)} opportunities with PH Assigned but NO SA Assigned.")
        
        # Analyze their workflow statuses
        status_counts = {}
        for opp in ph_assigned_no_sa:
            status = opp.workflow_status or "None"
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("\nWorkflow Status Distribution for these opportunities:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
            
        # Check against the filter list in the code
        # The filter is: ['NEW', 'OPEN', 'HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', None, '']
        allowed_statuses = ['NEW', 'OPEN', 'HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', None, '']
        
        print("\nOpportunities blocked by current filter:")
        blocked_count = 0
        for opp in ph_assigned_no_sa:
            status = opp.workflow_status
            if status not in allowed_statuses:
                print(f"  ID: {opp.opp_id} | Status: {status} | PH: {opp.assigned_practice_head_id}")
                blocked_count += 1
                
        if blocked_count == 0:
            print("  None found blocked by status filter.")
        else:
            print(f"  Total Blocked: {blocked_count}")

    finally:
        db.close()

if __name__ == "__main__":
    check_ph_assignments()
