import sys
import os

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity
from datetime import datetime, timezone

def test_db():
    init_db()
    db = SessionLocal()
    try:
        opp = Opportunity(
            opp_id="test_opt1",
            opp_number="123",
            opp_name="Test",
            customer_name="Customer",
            deal_value=0.0,
            stage="Open",
            close_date=datetime.now(),
            crm_last_updated_at=datetime.now(timezone.utc),
            # NOT setting workflow_status
        )
        db.add(opp)
        db.commit()
        print("Success")
    except Exception as e:
        db.rollback()
        print(f"Exception raised: {type(e).__name__} - {e}")

test_db()
