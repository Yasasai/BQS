
import sys
import os
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser

def debug_david_visibility():
    db = SessionLocal()
    try:
        # 1. Get David
        david = db.query(AppUser).filter(AppUser.display_name == "David Chen").first()
        if not david:
            print("❌ David Chen not found!")
            return
        
        print(f"👤 David Chen: {david.user_id} (Role: PH typically)")

        # 2. Check Assignments directly
        direct_assignments = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == david.user_id).all()
        print(f"\n📋 Direct Assignments in DB: {len(direct_assignments)}")
        for o in direct_assignments:
            print(f"   - {o.opp_name} ({o.opp_id}) [Status: {o.workflow_status}]")

        # 3. Simulate the API Query Logic for 'action-required' tab
        # Logic from opportunities.py:
        # role == 'PH'
        # user_id == david.user_id
        # tab == 'action-required' -> workflow_status not in comp_stats + assigned_sa_id is None
        
        comp_stats = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']
        rev_stats = ['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']
        targets = ['RetailCo', 'Acme']
        safety_hatch = or_(*[Opportunity.opp_name.ilike(f'%{t}%') for t in targets])

        base_query = db.query(Opportunity).filter(Opportunity.is_active == True)
        
        # Role Filter
        role_filtered = base_query.filter(or_(Opportunity.assigned_practice_head_id == david.user_id, safety_hatch))
        print(f"\n🔍 Items visible after Role Filter (Assigned OR Safety): {role_filtered.count()}")
        
        # Tab Filter: Action Required
        # f_comp = ph_approval_status in ['APPROVED', 'REJECTED'] ... actually logic is complex in backend.
        # Let's look at the specific tab logic from backend/app/routers/opportunities.py
        
        # "action-required" for PH means:
        # not in comp_stats AND assigned_sa_id is None
        
        ar_query = role_filtered.filter(Opportunity.workflow_status.notin_(comp_stats))
        ar_query = ar_query.filter(Opportunity.assigned_sa_id.is_(None))
        
        print(f"   - Action Required Tab Count: {ar_query.count()}")
        for o in ar_query.all():
            print(f"     -> {o.opp_name} (SA: {o.assigned_sa_id})")

    finally:
        db.close()

if __name__ == "__main__":
    debug_david_visibility()
