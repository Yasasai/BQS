
import os
import sys
from datetime import datetime
import uuid

# Setup paths
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import OppScoreVersion, OppScoreSectionValue, Opportunity, AppUser

def test_submission():
    db = SessionLocal()
    try:
        # 1. Get a user
        user = db.query(AppUser).first()
        if not user:
            print("No user found. Seeding first...")
            init_db()
            user = db.query(AppUser).first()
        
        # 2. Get an opportunity
        opp = db.query(Opportunity).first()
        if not opp:
            print("No opportunity found. Creating dummy...")
            opp = Opportunity(
                opp_id="TEST-123",
                opp_name="Test Opty",
                customer_name="Test Customer",
                crm_last_updated_at=datetime.utcnow()
            )
            db.add(opp)
            db.commit()
            db.refresh(opp)
        
        print(f"Testing for Opp: {opp.opp_id} and User: {user.email}")
        
        # 3. Create Version
        version = OppScoreVersion(
            opp_id=opp.opp_id,
            version_no=1,
            status="SUBMITTED",
            created_by_user_id=user.user_id,
            overall_score=85
        )
        db.add(version)
        db.flush()
        
        # 4. Create Section Values
        val = OppScoreSectionValue(
            score_version_id=version.score_version_id,
            section_code="STRAT",
            score=4.5,
            notes="Strong strategic fit",
            selected_reasons=["Strategic Alignment"]
        )
        db.add(val)
        
        db.commit()
        print("✅ Mock submission successful!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Mock submission FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_submission()
