
import os
import sys
from datetime import datetime

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

from backend.oracle_service import get_from_oracle, map_oracle_to_db
from backend.database import SessionLocal, Opportunity, OpportunityDetails, init_db

def sync_specific_id(target_id="1602736"):
    print(f"🎯 Targeting Opportunity ID: {target_id}...")
    
    # 1. Fetch from Oracle
    # We use RecordSet='ALL' to ensure visibility
    params = {
        "q": f"RecordSet='ALL';OptyNumber='{target_id}' OR OptyId='{target_id}'",
        "onlyData": "true",
        "limit": 1
    }
    
    data = get_from_oracle("opportunities", params=params)
    
    if "error" in data:
        print(f"❌ Oracle API Error: {data['error']}")
        return

    items = data.get("items", [])
    if not items:
        print(f"⚠️  Opportunity {target_id} not found in Oracle. Please check if your user has access to this record.")
        return

    oracle_item = items[0]
    print(f"✅ Found: {oracle_item.get('Name')}")

    # 2. Map and Save to PostgreSQL
    init_db()
    db = SessionLocal()
    try:
        mapped = map_oracle_to_db(oracle_item)
        primary_data = mapped["primary"]
        detail_data = mapped["details"]

        # Upsert Primary
        existing = db.query(Opportunity).filter(Opportunity.remote_id == str(primary_data['remote_id'])).first()
        if existing:
            for key, val in primary_data.items():
                setattr(existing, key, val)
            print(f"💾 Updated existing record in 'opportunities' table.")
        else:
            db.add(Opportunity(**primary_data))
            print(f"💾 Inserted new record into 'opportunities' table.")

        # Upsert Details
        existing_detail = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == str(primary_data['remote_id'])).first()
        if existing_detail:
            for key, val in detail_data.items():
                setattr(existing_detail, key, val)
        else:
            db.add(OpportunityDetails(**detail_data))

        db.commit()
        print(f"🚀 SUCCESS: Opportunity {target_id} is now synced to PostgreSQL.")

    except Exception as e:
        print(f"❌ Sync Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_specific_id("1602736")
