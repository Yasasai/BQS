
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import or_

def verify_action_required():
    db = SessionLocal()
    try:
        # Find Sarah (PH)
        sarah = db.query(AppUser).filter(AppUser.display_name.ilike('%Sarah%')).first()
        if not sarah:
            print("Sarah not found")
            return

        print(f"Checking for Sarah (PH, ID: {sarah.user_id})")
        
        # New Logic: Assigned to PH, SA is None, Status NOT CLOSED
        closed_statuses = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']
        
        query = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id == sarah.user_id,
            Opportunity.assigned_sa_id.is_(None),
            or_(
                Opportunity.workflow_status.notin_(closed_statuses),
                Opportunity.workflow_status.is_(None)
            )
        )
        
        count = query.count()
        print(f"Action Required Count (New Logic): {count}")
        
        items = query.limit(10).all()
        for item in items:
            print(f" - {item.opp_id} | Status: {item.workflow_status} | SA: {item.assigned_sa_id}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_action_required()
