import sys
import os
import uuid
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print("STARTING TEST...", flush=True)

# Add root to python path
# Assuming this script is in backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # Should be BQS/
sys.path.append(parent_dir)

from backend.app.database import Base
from backend.app.models import AppUser, Opportunity, OppScoreSection, OppScoreVersion, OppScoreSectionValue
from backend.app.routers.scoring import ScoreInput, SectionInput, submit_score

# Setup Independent DB Connection (to avoid messing with running app if possible, or just reuse)
# We will use the same DB string but maybe different session
from backend.app.database import SessionLocal, engine

db = SessionLocal()

def create_test_user(role, name):
    uid = f"TEST_{role}_{uuid.uuid4().hex[:8]}"
    u = AppUser(user_id=uid, email=f"{uid}@test.com", display_name=name)
    # Role handling might be complex if using separate tables, but for scoring router we just need AppUser
    # Wait, scoring router checks role?
    # No, scoring router just checks if user_id matches assigned_sa/sp_id
    db.add(u)
    db.commit()
    return u

def create_test_opp(sa_id, sp_id):
    oid = f"OPP-TEST-{uuid.uuid4().hex[:8]}"
    o = Opportunity(
        opp_id=oid, 
        opp_name="Combined Test Opp", 
        assigned_sa_id=sa_id, 
        assigned_sp_id=sp_id,
        workflow_status="ASSIGNED_TO_SA"
    )
    db.add(o)
    db.commit()
    return o

def create_score_input(user_id):
    # Get sections
    sections = db.query(OppScoreSection).all()
    if not sections:
        # Create dummy sections if empty
        s1 = OppScoreSection(section_code="TEST_SEC", section_name="Test Section", weight=1.0, display_order=1)
        db.add(s1)
        db.commit()
        sections = [s1]
        
    inputs = []
    for s in sections:
        inputs.append(SectionInput(section_code=s.section_code, score=4.0, notes="Test Note", selected_reasons=[]))
        
    return ScoreInput(
        user_id=user_id,
        sections=inputs,
        confidence_level="HIGH",
        recommendation="PURSUE",
        summary_comment="Test Submission",
        attachment_name=None
    )

def run_test():
    try:
        print("Creating users...")
        sa = create_test_user("SA", "Test SA")
        sp = create_test_user("SP", "Test SP")
        
        print("Creating opportunity...")
        opp = create_test_opp(sa.user_id, sp.user_id)
        print(f"Created Opp: {opp.opp_id}")
        
        print(f"Submitting Score for SA: {sa.user_id}")
        inp_sa = create_score_input(sa.user_id)
        submit_score(opp.opp_id, inp_sa, db)
        
        # Reload opp
        db.refresh(opp)
        print(f"Status after SA submit: {opp.workflow_status} (Expected: SA_SUBMITTED)")
        
        print(f"Submitting Score for SP: {sp.user_id}")
        inp_sp = create_score_input(sp.user_id)
        submit_score(opp.opp_id, inp_sp, db)
        
        # Reload opp
        db.refresh(opp)
        print(f"Status after SP submit: {opp.workflow_status}")
        print(f"Combined Ready: {opp.combined_submission_ready}")
        
        if opp.workflow_status == "READY_FOR_REVIEW" and opp.combined_submission_ready:
            print("\nSUCCESS: Combined Review Logic Verified!")
        else:
            print("\nFAILURE: Status not updated correctly.")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
