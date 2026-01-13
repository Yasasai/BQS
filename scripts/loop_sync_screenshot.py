
import os
import sys
import time
from datetime import datetime

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

from backend.oracle_service import fetch_single_opportunity, map_oracle_to_db
from backend.database import SessionLocal, Opportunity, OpportunityDetails, SyncLog, init_db

def loop_sync_screenshot_ids():
    target_ids = [
        "1602737", "1602738", "1693827", "1658743", "1658758", 
        "1657755", "1744044", "1754130", "1759271", "1755209", "1733846"
    ]
    
    print(f"🔄 Starting Master Sync Loop for {len(target_ids)} Opportunities...")
    init_db()
    db = SessionLocal()
    
    # Create a visible log entry for the UI
    sync_log = SyncLog(
        sync_type='SCREENSHOT_LOOP',
        status='RUNNING',
        started_at=datetime.utcnow(),
        total_fetched=len(target_ids)
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)
    
    success_count = 0
    fail_count = 0
    updated_count = 0
    new_count = 0
    
    try:
        for opty_id in target_ids:
            print(f"🔍 [{opty_id}] Fetching...", end=" ", flush=True)
            try:
                oracle_data = fetch_single_opportunity(opty_id)
                if not oracle_data:
                    print("⚠️  MISSING")
                    fail_count += 1
                    continue
                
                print(f"✅ Found ({oracle_data.get('Name', '...')[:20]})")
                mapped = map_oracle_to_db(oracle_data)
                primary = mapped["primary"]
                details = mapped["details"]
                
                existing = db.query(Opportunity).filter(Opportunity.remote_id == str(opty_id)).first()
                if existing:
                    for key, val in primary.items(): setattr(existing, key, val)
                    updated_count += 1
                else:
                    db.add(Opportunity(**primary, workflow_status='NEW_FROM_CRM'))
                    new_count += 1
                
                # Update details
                existing_details = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == str(opty_id)).first()
                if existing_details:
                    for key, val in details.items(): setattr(existing_details, key, val)
                else:
                    db.add(OpportunityDetails(**details))
                
                db.commit()
                success_count += 1
                
                # Update progress in live log
                sync_log.new_records = new_count
                sync_log.updated_records = updated_count
                sync_log.failed_records = fail_count
                db.commit()
                
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ ERROR: {e}")
                db.rollback()
                fail_count += 1
        
        sync_log.status = 'SUCCESS'
        sync_log.completed_at = datetime.utcnow()
        db.commit()
        print(f"\n✅ COMPLETED: {success_count} synced, {fail_count} failed.")
    except Exception as e:
        sync_log.status = 'FAILED'
        sync_log.error_message = str(e)
        db.commit()
        print(f"❌ GLOBAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    loop_sync_screenshot_ids()
