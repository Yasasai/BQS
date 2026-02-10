
import sys
import os
sys.path.append(os.getcwd())
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OppScoreVersion
from sqlalchemy import desc

def fix_fast_track():
    db = SessionLocal()
    try:
        # Find all opportunities that are not finalized but have a score in the 3.5-4.0 range
        opps = db.query(Opportunity).filter(
            Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'SUBMITTED', 'PENDING_FINAL_APPROVAL'])
        ).all()
        
        count = 0
        for opp in opps:
            latest_ver = db.query(OppScoreVersion).filter(
                OppScoreVersion.opp_id == opp.opp_id
            ).order_by(desc(OppScoreVersion.version_no)).first()
            
            if latest_ver and latest_ver.overall_score:
                score_5 = (latest_ver.overall_score / 100.0) * 5.0
                if 3.5 <= score_5 < 4.0:
                    print(f"Fixing Fast-Track for {opp.opp_number} ({opp.opp_name}) - Score: {score_5}")
                    opp.workflow_status = 'PENDING_GH_APPROVAL'
                    if opp.ph_approval_status == 'PENDING': opp.ph_approval_status = 'NOTIFIED'
                    if opp.sh_approval_status == 'PENDING': opp.sh_approval_status = 'NOTIFIED'
                    count += 1
        
        db.commit()
        print(f"Successfully updated {count} opportunities to Fast-Track status.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_fast_track()
