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

def fix_all_statuses():
    print("🔍 Starting comprehensive status fix for ALL opportunities...")
    
    opps = session.query(Opportunity).all()
    users = {u.user_id: u.role for u in session.query(AppUser).all()}
    
    fixed_count = 0
    
    for opp in opps:
        # Get latest score
        latest_ver = session.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp.opp_id
        ).order_by(desc(OppScoreVersion.version_no)).first()
        
        # If no score, skip specific submission checks, but maybe check generic consistency?
        if not latest_ver:
            # Ensure workflow status isn't stuck in a 'submitted' state if no version exists
            if opp.workflow_status in ['SUBMITTED', 'SA_SUBMITTED', 'SP_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW']:
                # This would be weird data corruption. Let's ignore for now or log it.
                pass
            continue

        # If we have a version, let's check its status
        score_status = latest_ver.status
        
        if score_status == 'SUBMITTED':
            # Identify who submitted this specific version
            submitter_role = users.get(latest_ver.created_by_user_id, 'UNKNOWN')
            
            # --- Determine Correct Workflow Status ---
            # 1. Start with current assignments
            is_sa_assigned = opp.assigned_sa_id is not None
            is_sp_assigned = opp.assigned_sp_id is not None
            
            # 2. Check submission flags on the version (if they exist/are reliable)
            # The backend logic uses 'sa_submitted' and 'sp_submitted' flags on the version object
            ver_sa_sub = latest_ver.sa_submitted
            ver_sp_sub = latest_ver.sp_submitted
            
            # If flags are missing/false but status is SUBMITTED, infer from submitter role
            if not ver_sa_sub and not ver_sp_sub:
                if submitter_role == 'SA': ver_sa_sub = True
                if submitter_role == 'SP': ver_sp_sub = True
            
            # 3. Check for existence of ANY submitted version by the "other" role
            # (e.g. if this version is by SP, did SA submit a previous one?)
            if not ver_sa_sub and is_sa_assigned:
                 # Search for any submitted version by this SA
                 other = session.query(OppScoreVersion).filter(
                     OppScoreVersion.opp_id == opp.opp_id,
                     OppScoreVersion.created_by_user_id == opp.assigned_sa_id,
                     OppScoreVersion.status == 'SUBMITTED'
                 ).first()
                 if other: ver_sa_sub = True

            if not ver_sp_sub and is_sp_assigned:
                 other = session.query(OppScoreVersion).filter(
                     OppScoreVersion.opp_id == opp.opp_id,
                     OppScoreVersion.created_by_user_id == opp.assigned_sp_id,
                     OppScoreVersion.status == 'SUBMITTED'
                 ).first()
                 if other: ver_sp_sub = True
            
            # 4. Calculate Expected Status
            expected_status = 'READY_FOR_REVIEW' # Default fully complete
            
            if is_sa_assigned and is_sp_assigned:
                if ver_sa_sub and ver_sp_sub:
                    expected_status = 'READY_FOR_REVIEW'
                elif ver_sa_sub:
                    expected_status = 'SA_SUBMITTED'
                elif ver_sp_sub:
                    expected_status = 'SP_SUBMITTED'
                else:
                    # Generic fallback if neither? Should imply one IS submitted given 'score_status == SUBMITTED'
                    if submitter_role == 'SA': expected_status = 'SA_SUBMITTED'
                    elif submitter_role == 'SP': expected_status = 'SP_SUBMITTED'
            
            elif is_sa_assigned:
                # Only SA assigned
                if ver_sa_sub: expected_status = 'READY_FOR_REVIEW' # Sole contributor done
                elif submitter_role == 'SA': expected_status = 'READY_FOR_REVIEW'
                
            elif is_sp_assigned:
                # Only SP assigned
                if ver_sp_sub: expected_status = 'READY_FOR_REVIEW'
                elif submitter_role == 'SP': expected_status = 'READY_FOR_REVIEW'
            
            else:
                # No one assigned?
                expected_status = 'READY_FOR_REVIEW'

            # 5. Apply Fast Track Logic if applicable (Score 3.5-4.0) -> PENDING_GH_APPROVAL
            # Calculate raw score 5-scale
            # (Simplified check: if backend calculated generic 'READY_FOR_REVIEW', it might actually be 'PENDING_GH_APPROVAL')
            # For this script, let's trust 'READY_FOR_REVIEW' is a good enough bucket unless we want to recalc scores.
            # 'PENDING_GH_APPROVAL' is technically a subset of ready-for-review state.
            
            # 6. Compare and Update
            current_status = opp.workflow_status
            
            # Normalize legacy 'SUBMITTED'
            if current_status == 'SUBMITTED':
                # Force update
                print(f"🔄 Updating '{opp.opp_name}' from legacy SUBMITTED to {expected_status}")
                opp.workflow_status = expected_status
                fixed_count += 1
            elif current_status != expected_status:
                # Only update if specifically distinct and valid transition
                # e.g. don't downgrade 'PENDING_GH_APPROVAL' to 'READY_FOR_REVIEW'
                if current_status == 'PENDING_GH_APPROVAL' and expected_status == 'READY_FOR_REVIEW':
                    pass 
                elif current_status in ['APPROVED', 'REJECTED', 'WON', 'COMPLETED']:
                    pass # Don't reopen closed opps
                else:
                    print(f"🔧 Fixing '{opp.opp_name}': {current_status} -> {expected_status}")
                    opp.workflow_status = expected_status
                    fixed_count += 1

        # 7. Ensure Approval Statuses are Clean (Not NULL)
        dirty_approval = False
        if opp.gh_approval_status is None: 
            opp.gh_approval_status = 'PENDING'
            dirty_approval = True
        if opp.ph_approval_status is None: 
            opp.ph_approval_status = 'PENDING'
            dirty_approval = True
        if opp.sh_approval_status is None: 
            opp.sh_approval_status = 'PENDING'
            dirty_approval = True
            
        if dirty_approval:
            # We count this as a fix only if we didn't already count it
            # (No simple way to track double-count in this loop structure without flag, but it's fine)
            pass

    session.commit()
    print(f"✅ Scanning complete. {fixed_count} opportunities updated.")

from sqlalchemy import or_

def fix_stuck_null_statuses():
    # Fix opps that have NO status at all (NULL) but might be in progress
    print("🧹 Cleaning up NULL workflow statuses...")
    null_opps = session.query(Opportunity).filter(
        or_(Opportunity.workflow_status.is_(None), Opportunity.workflow_status == '')
    ).all()
    
    for opp in null_opps:
        print(f"   Set default 'NEW' for NULL status opp: {opp.opp_name}")
        opp.workflow_status = 'NEW'
    
    session.commit()

if __name__ == "__main__":
    fix_all_statuses()
    fix_stuck_null_statuses()
