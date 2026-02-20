
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import or_, and_

def verify_waterfall():
    db = SessionLocal()
    try:
        # 1. Identify Sarah (PH)
        sarah = db.query(AppUser).filter(AppUser.display_name.ilike('%Sarah%')).first()
        if not sarah:
            print("Sarah not found")
            return

        print(f"Verifying Waterfall Logic for: {sarah.display_name} (ID: {sarah.user_id})")
        print("-" * 60)
        
        # Re-implement the same waterfall logic here to verify against DB
        filter_completed = Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED'])
        
        filter_review = and_(
             ~filter_completed,
             Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']),
             Opportunity.ph_approval_status == 'PENDING'
        )
        
        filter_in_progress = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sa_id.isnot(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        filter_action = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sa_id.is_(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )

        # Base Query
        base_query = db.query(Opportunity).filter(
             Opportunity.is_active == True,
             Opportunity.assigned_practice_head_id == sarah.user_id
        )

        c_completed = base_query.filter(filter_completed).count()
        c_review = base_query.filter(filter_review).count()
        c_progress = base_query.filter(filter_in_progress).count()
        c_action = base_query.filter(filter_action).count()
        
        total_assigned = base_query.count()
        
        print(f"Total Assigned: {total_assigned}")
        print(f" - Completed: {c_completed}")
        print(f" - Review: {c_review}")
        print(f" - In Progress: {c_progress}")
        print(f" - Action Required: {c_action}")
        print(f"Sum Check: {c_completed + c_review + c_progress + c_action}")
        
        if (c_completed + c_review + c_progress + c_action) != total_assigned:
            print("⚠️ WARNING: Sum mismatched! Some opportunities are falling through the cracks.")
            # Find the missing ones
            all_opps = base_query.all()
            for o in all_opps:
                 # Check which bucket it falls into manually
                 pass # Logic too complex to repeat inline, relying on counts
        else:
            print("✅ Sum Matches. No opportunities lost.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_waterfall()
