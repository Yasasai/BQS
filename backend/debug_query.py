from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func, or_, and_
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models import Opportunity, OppScoreVersion, AppUser
from app.core.database import Base

# Database setup
DATABASE_URL = "sqlite:///backend/bqs.db"
engine = create_engine(DATABASE_URL)
session = Session(engine)

def debug_review_query():
    print("🕵️ Debugging Review Query Logic...")
    
    # 1. Define Filter logic exactly as in opportunities.py
    # PH Logic
    ph_user_id = 'ph-001'
    print(f"\n--- Checking for PH: {ph_user_id} ---")
    
    base_query = session.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.assigned_practice_head_id == ph_user_id
    )
    
    total_assigned = base_query.count()
    print(f"Total Assigned to {ph_user_id}: {total_assigned}")
    
    filter_completed = Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED'])
    
    filter_review = and_(
         ~filter_completed,
         Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
         or_(Opportunity.ph_approval_status == 'PENDING', Opportunity.ph_approval_status.is_(None))
    )
    
    review_opps = base_query.filter(filter_review).all()
    print(f"Review Count: {len(review_opps)}")
    for opp in review_opps:
        print(f"  - {opp.opp_name} (Status: {opp.workflow_status}, PH Status: {opp.ph_approval_status})")

    # SH Logic
    sh_user_id = 'sh-001'
    print(f"\n--- Checking for SH: {sh_user_id} ---")
    
    base_query_sh = session.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.assigned_sales_head_id == sh_user_id
    )
    
    total_assigned_sh = base_query_sh.count()
    print(f"Total Assigned to {sh_user_id}: {total_assigned_sh}")
    
    filter_completed_sh = Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED'])
    
    filter_review_sh = and_(
         ~filter_completed_sh,
         Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
         or_(Opportunity.sh_approval_status == 'PENDING', Opportunity.sh_approval_status.is_(None))
    )
    
    review_opps_sh = base_query_sh.filter(filter_review_sh).all()
    print(f"Review Count: {len(review_opps_sh)}")
    for opp in review_opps_sh:
        print(f"  - {opp.opp_name} (Status: {opp.workflow_status}, SH Status: {opp.sh_approval_status})")
    
    # GH Logic
    print("\n--- Checking for GH (Role='GH') ---")
    gh_query = session.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
        or_(Opportunity.gh_approval_status == 'PENDING', Opportunity.gh_approval_status.is_(None))
    )
    
    review_opps_gh = gh_query.all()
    print(f"Review Count for GH: {len(review_opps_gh)}")
    found_acme = False
    for opp in review_opps_gh:
        if 'Acme' in opp.opp_name: found_acme = True
        # print(f"  - {opp.opp_name}") # Too many potentially
    
    if found_acme: print("✅ Acme found in GH list.")
    else: print("❌ Acme NOT found in GH list.")

if __name__ == "__main__":
    debug_review_query()
