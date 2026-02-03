
import os
import sys
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path: .../backend/app/services/sync_manager.py -> .../
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
def log(msg): 
    print(msg, flush=True)
    logging.info(msg)

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity, Practice

def map_oracle_to_db(item, db: Session):
    """Map Oracle JSON to our Opportunity model"""
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id: return None
        
        # Parse dates
        last_update_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
        crm_last_updated_at = datetime.utcnow()
        if last_update_str:
            try:
                crm_last_updated_at = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            except: pass
            
        close_date = None
        if item.get("EffectiveDate"):
            try:
                close_date = datetime.strptime(item["EffectiveDate"][:10], "%Y-%m-%d")
            except: pass

        # Practice lookup/create
        primary_practice_id = None
        practice_val = item.get("Practice_c")
        if practice_val:
            prac = db.query(Practice).filter(Practice.practice_name == practice_val).first()
            if not prac:
                import uuid
                prac = Practice(
                    practice_id=str(uuid.uuid4()),
                    practice_code=practice_val.upper().replace(" ", "_")[:20],
                    practice_name=practice_val
                )
                db.add(prac)
                db.flush()
            primary_practice_id = prac.practice_id

        return {
            "opp_id": opty_id,
            "opp_number": str(item.get("OptyNumber") or opty_id),
            "opp_name": item.get("Name") or "Unknown Opportunity",
            "customer_name": item.get("TargetPartyName") or "Unknown Account",
            "geo": item.get("GEO_c") or item.get("Geo_c") or item.get("Region_c"),
            "currency": item.get("CurrencyCode", "USD"),
            "deal_value": float(item.get("Revenue") or 0),
            "stage": item.get("SalesStage"),
            "close_date": close_date,
            "crm_last_updated_at": crm_last_updated_at,
            "primary_practice_id": primary_practice_id,
            "is_active": True
        }
    except Exception as e:
        log(f"⚠️ Mapping Error: {e}")
        return None

def sync_opportunities():
    """
    Fetches ALL opportunities using RecordSet='ALL' with proper field names.
    """
    log("🚀 Starting CLEAN Dynamic Sync...")
    
    init_db()
    db = SessionLocal()
    
    # 1. Base URL
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
    
    # 2. Batch settings - Process 10 records at a time
    limit = 10  # Batch size
    offset = 0
    total_saved = 0
    batch_number = 1
    has_more = True
    
    with httpx.Client(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        while has_more:
            log(f"\n{'='*70}")
            log(f"📦 BATCH {batch_number}: Fetching records {offset} to {offset + limit - 1}")
            log(f"{'='*70}")
            
            # 3. USER'S EXACT URL FORMAT
            # Using MyOpportunitiesFinder with RecordSet='ALLOPTIES'
            url = (
                f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
                f"?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
                f"&limit={limit}"
                f"&offset={offset}"
            )
            
            # Log the EXACT URL being sent
            log(f"🔗 Requesting: {url}")
            
            try:
                # 4. Make Request (NO params argument - URL is complete)
                response = client.get(url)
                
                if response.status_code != 200:
                    log(f"❌ API Error: {response.status_code} - {response.text[:200]}")
                    break
                
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    log("✅ No more items found.")
                    has_more = False
                    break
                
                log(f"📝 Processing {len(items)} items in this batch...")
                
                # 5. Process each item
                batch_saved = 0
                for item in items:
                    mapped = map_oracle_to_db(item, db)
                    if not mapped:
                        continue
                    
                    try:
                        existing = db.query(Opportunity).filter(
                            Opportunity.opp_id == mapped["opp_id"]
                        ).first()
                        
                        if existing:
                            for k, v in mapped.items():
                                setattr(existing, k, v)
                        else:
                            db.add(Opportunity(**mapped))
                        
                        db.commit()
                        batch_saved += 1
                        total_saved += 1
                        print(f"   ✓ Saved: {mapped['opp_name'][:50]}")
                        
                    except Exception as e:
                        db.rollback()
                        log(f"⚠️ DB Error: {e}")
                
                log(f"✅ Batch {batch_number} complete: {batch_saved}/{len(items)} saved")
                log(f"📊 Total saved so far: {total_saved}")
                
                # 6. Pagination Check
                if len(items) < limit:
                    has_more = False
                else:
                    offset += limit
                    batch_number += 1
                
            except Exception as e:
                log(f"💥 Request Error: {e}")
                break
    
    db.close()
    log(f"🎉 Sync Complete! Total Saved: {total_saved} opportunities")
    return total_saved

if __name__ == "__main__":
    sync_opportunities()
