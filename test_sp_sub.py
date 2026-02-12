
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser, OppScoreVersion

def test_sp_submission():
    db = SessionLocal()
    try:
        sp_id = 'sp-001'
        # Find an opp assigned to this SP
        opp = db.query(Opportunity).filter(Opportunity.assigned_sp_id == sp_id).first()
        if not opp:
            print("No Opp found for SP.")
            return

        print(f"Testing submission for Opp: {opp.opp_id} | Name: {opp.opp_name}")
        
        # 1. Create a draft if not exists
        draft = db.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp.opp_id,
            OppScoreVersion.created_by_user_id == sp_id
        ).first()
        
        if not draft:
            draft = OppScoreVersion(
                opp_id=opp.opp_id,
                version_no=1,
                status="UNDER_ASSESSMENT",
                created_by_user_id=sp_id
            )
            db.add(draft)
            db.commit()
            print("Created draft.")

        # 2. Simulate POST to submit
        import requests
        url = f"http://127.0.0.1:8000/api/scoring/{opp.opp_id}/submit"
        payload = {
            "user_id": sp_id,
            "sections": [
                {"section_code": "STRAT", "score": 4.0, "notes": "Test notes", "selected_reasons": ["Strategic Account"]}
            ],
            "confidence_level": "HIGH",
            "recommendation": "PURSUE",
            "summary_comment": "Testing SP submission from script. Mandatory 20 chars."
        }
        
        # We need the backend to be running. If it's not, we just call the function directly.
        from backend.app.routers.scoring import submit_score, ScoreInput, SectionInput
        
        data = ScoreInput(
            user_id=sp_id,
            sections=[SectionInput(section_code="STRAT", score=4.0, notes="Test notes", selected_reasons=["Strategic Account"])],
            confidence_level="HIGH",
            recommendation="PURSUE",
            summary_comment="Testing SP submission from script. Mandatory 20 chars."
        )
        
        print("Calling submit_score...")
        res = submit_score(opp.opp_id, data, db)
        print(f"Result: {res}")
        
        # Verify Opportunity status
        db.refresh(opp)
        print(f"New Opportunity Workflow Status: {opp.workflow_status}")

    finally:
        db.close()

if __name__ == "__main__":
    test_sp_submission()
