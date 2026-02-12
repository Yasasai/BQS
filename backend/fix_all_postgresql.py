from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func, or_, and_
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Use the REAL database settings from the app
from app.models import Opportunity, OppScoreVersion, AppUser
from app.core.database import DATABASE_URL

print(f"Connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
session = Session(engine)

def fix_all_postgresql():
    print("🔍 Starting comprehensive status fix for PostgreSQL BQS database...")
    
    opps = session.query(Opportunity).all()
    users = {u.user_id: u.role for u in session.query(AppUser).all()}
    
    fixed_count = 0
    
    for opp in opps:
        # 1. Ensure Approval Statuses are 'PENDING' instead of NULL
        dirty = False
        if opp.gh_approval_status is None:
            opp.gh_approval_status = 'PENDING'
            dirty = True
        if opp.ph_approval_status is None:
            opp.ph_approval_status = 'PENDING'
            dirty = True
        if opp.sh_approval_status is None:
            opp.sh_approval_status = 'PENDING'
            dirty = True
            
        # 2. Fix Workflow Status based on submission history
        latest_ver = session.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp.opp_id
        ).order_by(desc(OppScoreVersion.version_no)).first()
        
        if latest_ver and latest_ver.status == 'SUBMITTED':
            submitter_role = users.get(latest_ver.created_by_user_id, 'UNKNOWN')
            
            # Revisit status logic
            is_sa_assigned = opp.assigned_sa_id is not None
            is_sp_assigned = opp.assigned_sp_id is not None
            
            # Simple flags
            ver_sa_sub = latest_ver.sa_submitted
            ver_sp_sub = latest_ver.sp_submitted
            
            # Inferred flags
            if not ver_sa_sub and not ver_sp_sub:
                if submitter_role == 'SA': ver_sa_sub = True
                if submitter_role == 'SP': ver_sp_sub = True
                
            # Cross-check other submissions
            if not ver_sa_sub and is_sa_assigned:
                if session.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp.opp_id, OppScoreVersion.created_by_user_id == opp.assigned_sa_id, OppScoreVersion.status == 'SUBMITTED').first():
                    ver_sa_sub = True
            if not ver_sp_sub and is_sp_assigned:
                if session.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp.opp_id, OppScoreVersion.created_by_user_id == opp.assigned_sp_id, OppScoreVersion.status == 'SUBMITTED').first():
                    ver_sp_sub = True
            
            # Calculate correct status
            new_status = opp.workflow_status
            
            if is_sa_assigned and is_sp_assigned:
                if ver_sa_sub and ver_sp_sub: new_status = 'READY_FOR_REVIEW'
                elif ver_sa_sub: new_status = 'SA_SUBMITTED'
                elif ver_sp_sub: new_status = 'SP_SUBMITTED'
            elif is_sa_assigned:
                if ver_sa_sub: new_status = 'READY_FOR_REVIEW'
            elif is_sp_assigned:
                if ver_sp_sub: new_status = 'READY_FOR_REVIEW'
            else:
                new_status = 'READY_FOR_REVIEW'
            
            if opp.workflow_status != new_status and opp.workflow_status not in ['APPROVED', 'REJECTED']:
                print(f"🔧 Updating {opp.opp_name}: {opp.workflow_status} -> {new_status}")
                opp.workflow_status = new_status
                dirty = True
        
        # Ensure 'NULL' workflow status becomes 'NEW'
        if opp.workflow_status is None or opp.workflow_status == '':
            opp.workflow_status = 'NEW'
            dirty = True
            
        if dirty:
            fixed_count += 1

    session.commit()
    print(f"✅ Scanning complete. {fixed_count} opportunities updated in PostgreSQL.")

if __name__ == "__main__":
    fix_all_postgresql()
