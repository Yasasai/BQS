
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
from sqlalchemy import or_

def check_orphaned_opportunities():
    db = SessionLocal()
    try:
        # PH perspective: Assigned SA but status not advanced enough for "In Progress"
        ph_orphans = db.query(Opportunity).filter(
            Opportunity.assigned_sa_id.isnot(None),
            Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN'])
        ).all()
        
        print(f"Values found for PH Orphans: {len(ph_orphans)}")
        for opp in ph_orphans:
            print(f"PH Orphan: {opp.opp_id} | Status: {opp.workflow_status} | SA: {opp.assigned_sa_id} | SP: {opp.assigned_sp_id}")

        # SH perspective: Assigned SP but status not advanced enough
        sh_orphans = db.query(Opportunity).filter(
            Opportunity.assigned_sp_id.isnot(None),
            Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN'])
        ).all()
        
        print(f"Values found for SH Orphans: {len(sh_orphans)}")
        for opp in sh_orphans:
            print(f"SH Orphan: {opp.opp_id} | Status: {opp.workflow_status} | SA: {opp.assigned_sa_id} | SP: {opp.assigned_sp_id}")

    finally:
        db.close()

if __name__ == "__main__":
    check_orphaned_opportunities()
