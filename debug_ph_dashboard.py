
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser
from sqlalchemy import or_

def debug_dashboard_logic():
    db = SessionLocal()
    try:
        # 1. Identify the Practice Head (Sarah)
        ph_user = db.query(AppUser).filter(AppUser.display_name.ilike('%Sarah%')).first()
        if not ph_user:
            print("❌ User 'Sarah' not found. Please check user list.")
            return

        print(f"👤 Debugging Dashboard for: {ph_user.display_name} (ID: {ph_user.user_id})")
        print("-" * 80)

        # 2. Fetch ALL active opportunities assigned to this PH
        opps = db.query(Opportunity).filter(
            Opportunity.assigned_practice_head_id == ph_user.user_id,
            Opportunity.is_active == True
        ).all()

        print(f"📚 Total Assigned Opportunities: {len(opps)}")
        print("-" * 80)
        print(f"{'Opp ID':<10} | {'Status':<20} | {'SA Assigned?':<12} | {'PH Approval':<12} | {'Proposed Tab':<15}")
        print("-" * 80)

        counts = {"action-required": 0, "in-progress": 0, "review": 0, "completed": 0, "MISSING": 0}

        for o in opps:
            # Simulate Logic
            tab = "MISSING"
            
            # Logic Definitions
            is_closed = o.workflow_status in ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']
            is_review = o.workflow_status in ['UNDER_REVIEW', 'READY_FOR_REVIEW']
            has_sa = o.assigned_sa_id is not None
            
            # 1. Completed
            if o.ph_approval_status in ['APPROVED', 'REJECTED']:
                tab = "completed"
            
            # 2. Review
            elif is_review and o.ph_approval_status == 'PENDING':
                tab = "review"
                
            # 3. In Progress (Has SA, not in review/completed)
            elif has_sa and not is_closed and not is_review:
                tab = "in-progress"
                
            # 4. Action Required (No SA, not closed)
            elif not has_sa and not is_closed:
                tab = "action-required"
            
            counts[tab] += 1
            
            print(f"{o.opp_id:<10} | {o.workflow_status or 'None':<20} | {str(bool(o.assigned_sa_id)):<12} | {o.ph_approval_status or 'None':<12} | {tab:<15}")

        print("-" * 80)
        print("📊 Simulated Counts:", counts)

    finally:
        db.close()

if __name__ == "__main__":
    debug_dashboard_logic()
