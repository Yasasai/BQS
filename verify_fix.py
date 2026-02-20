
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
from sqlalchemy import or_, and_

def verify_fix():
    db = SessionLocal()
    with open('verification_results.txt', 'w') as f:
        try:
            # Check for PH In-Progress candidates with new logic
            # Logic: status in [IN_ASSESSMENT, EXECUTORS_ASSIGNED, UNDER_ASSESSMENT] 
            # OR (assigned_sa is NOT None AND status in [HEADS_ASSIGNED, PH_ASSIGNED, SH_ASSIGNED, NEW, OPEN, None])
            
            ph_query = db.query(Opportunity).filter(
                or_(
                    Opportunity.workflow_status.in_(['IN_ASSESSMENT', 'EXECUTORS_ASSIGNED', 'UNDER_ASSESSMENT']),
                    and_(
                        Opportunity.assigned_sa_id.isnot(None),
                        Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN', None])
                    )
                )
            )
            ph_count = ph_query.count()
            f.write(f"PH In-Progress Count: {ph_count}\n")
            
            # Additional detail: find items that are ONLY caught by the new condition
            new_logic_only = db.query(Opportunity).filter(
                Opportunity.assigned_sa_id.isnot(None),
                Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN', None])
            ).all()
            
            f.write(f"Items saved by new logic (PH): {len(new_logic_only)}\n")
            for opp in new_logic_only:
                f.write(f" - {opp.opp_id}: Status={opp.workflow_status}, SA={opp.assigned_sa_id}\n")

            # Same for SH
            sh_query = db.query(Opportunity).filter(
                or_(
                    Opportunity.workflow_status.in_(['IN_ASSESSMENT', 'EXECUTORS_ASSIGNED', 'UNDER_ASSESSMENT']),
                    and_(
                        Opportunity.assigned_sp_id.isnot(None),
                        Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN', None])
                    )
                )
            )
            sh_count = sh_query.count()
            f.write(f"SH In-Progress Count: {sh_count}\n")
            
        except Exception as e:
            f.write(f"Error: {e}\n")
        finally:
            db.close()

if __name__ == "__main__":
    verify_fix()
