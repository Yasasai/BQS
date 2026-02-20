
from backend.database import SessionLocal, OppScoreVersion, Opportunity
from sqlalchemy import desc

def debug_opp(opp_id):
    db = SessionLocal()
    try:
        # Check Opportunity
        opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
        if opp:
            print(f"Opportunity: {opp.name}, Workflow Status: {opp.workflow_status}")
        else:
            print(f"Opportunity {opp_id} not found in Opportunity table.")

        # Check Score Versions
        versions = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).all()
        print(f"Found {len(versions)} score versions for {opp_id}")
        for v in versions:
            print(f"Version: {v.version_no}, Status: {v.status}, Created: {v.created_at}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_opp("300003780261059")
