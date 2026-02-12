from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models import Opportunity, OppScoreVersion, OpportunityAssignment, AppUser
from app.core.database import Base

# Database setup
DATABASE_URL = "sqlite:///backend/bqs.db"
engine = create_engine(DATABASE_URL)
session = Session(engine)

def fix_opportunity_statuses():
    print("🔍 Scanning for stuck opportunities...")
    
    # 1. Find inconsistencies
    # Opportunities that appear "Open" but have a "Submitted" score
    opps = session.query(Opportunity).all()
    
    fixed_count = 0
    
    for opp in opps:
        # Get latest score
        latest_ver = session.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp.opp_id
        ).order_by(desc(OppScoreVersion.version_no)).first()
        
        if not latest_ver:
            continue
            
        current_status = opp.workflow_status
        score_status = latest_ver.status
        
        # Logic to detect "stuck" submissions
        if score_status == 'SUBMITTED':
            # Case 1: Workflow status is NULL or NEW/OPEN
            if current_status in [None, '', 'NEW', 'OPEN', 'IN_ASSESSMENT', 'UNDER_ASSESSMENT']:
                print(f"⚠️  Fixing OPP: {opp.opp_name} ({opp.opp_number})")
                print(f"    Current Workflow: {current_status} | Score Status: {score_status}")
                
                # Determine correct status
                # Check if this is the ONLY submission or if we have both?
                
                is_sa_sub = False
                is_sp_sub = False
                
                # Check SA
                if opp.assigned_sa_id:
                     sa_v = session.query(OppScoreVersion).filter(
                        OppScoreVersion.opp_id == opp.opp_id,
                        OppScoreVersion.created_by_user_id == opp.assigned_sa_id,
                        OppScoreVersion.status == 'SUBMITTED'
                     ).first()
                     if sa_v: is_sa_sub = True
                
                # Check SP
                if opp.assigned_sp_id:
                     sp_v = session.query(OppScoreVersion).filter(
                        OppScoreVersion.opp_id == opp.opp_id,
                        OppScoreVersion.created_by_user_id == opp.assigned_sp_id,
                        OppScoreVersion.status == 'SUBMITTED'
                     ).first()
                     if sp_v: is_sp_sub = True
                     
                # Fallback: If unassigned but submitted, assume it's the submitter's role?
                if not opp.assigned_sa_id and not opp.assigned_sp_id:
                    # User likely edited plain opp.
                    # Default to READY_FOR_REVIEW if we can't distinguish?
                    # Or check user role of the submitter
                    submitter = session.query(AppUser).filter(AppUser.user_id == latest_ver.created_by_user_id).first()
                    if submitter:
                        if submitter.role == 'SA': is_sa_sub = True
                        if submitter.role == 'SP': is_sp_sub = True
                
                new_status = "READY_FOR_REVIEW"
                if is_sa_sub and not is_sp_sub:
                     # Check if SP is even assigned?
                     if opp.assigned_sp_id: new_status = "SA_SUBMITTED"
                     else: new_status = "READY_FOR_REVIEW" # If no SP needed/assigned, SA submission is enough?
                elif is_sp_sub and not is_sa_sub:
                     if opp.assigned_sa_id: new_status = "SP_SUBMITTED"
                     else: new_status = "READY_FOR_REVIEW"
                elif is_sa_sub and is_sp_sub:
                    new_status = "READY_FOR_REVIEW"
                else:
                    # Generic fallback
                    new_status = "READY_FOR_REVIEW"
                    
                print(f"    👉 Updating to: {new_status}")
                opp.workflow_status = new_status
                fixed_count += 1
                
        # Also check approval statuses (NULL -> PENDING is handled in code, but clean DB is better)
        if opp.gh_approval_status is None: opp.gh_approval_status = 'PENDING'
        if opp.ph_approval_status is None: opp.ph_approval_status = 'PENDING'
        if opp.sh_approval_status is None: opp.sh_approval_status = 'PENDING'

    session.commit()
    print(f"✅ Fixed {fixed_count} opportunities.")

if __name__ == "__main__":
    fix_opportunity_statuses()
