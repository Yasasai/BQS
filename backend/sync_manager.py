
import os
import sys
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
def log(msg): 
    print(msg, flush=True)
    logging.info(msg)

try:
    from backend.app.core.database import SessionLocal, init_db
    from backend.app.models import Opportunity, Practice
except ImportError:
    # Fallback/Direct run support
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    """CLEAN Dynamic Sync - Minimal params, maximum compatibility"""
    log("🚀 Starting CLEAN Dynamic Sync...")
    
    init_db()
    db = SessionLocal()
    
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    
    # Filter for OPEN opportunities using the specific version
    limit = 50
    offset = 0
    total_saved = 0
    
    with httpx.Client(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        while True:
            params = {
                "q": "StatusCode='OPEN'",
                "offset": offset,
                "limit": limit,
                "totalResults": "true"
            }
            
            log(f"📡 Fetching: Offset {offset}, Limit {limit}")
            
            try:
                response = client.get(endpoint, params=params)
                
                if response.status_code != 200:
                    log(f"❌ API Error: {response.status_code} - {response.text[:200]}")
                    break

                data = response.json()
                items = data.get("items", [])

                if not items:
                    log("✅ No more items found.")
                    break

                log(f"   Processing {len(items)} items...")

                # Process each item
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
                        total_saved += 1
                        print(f"   ✓ Saved: {mapped['opp_name'][:50]}")
                        
                    except Exception as e:
                        db.rollback()
                        log(f"⚠️ DB Error: {e}")

                # Check if more pages exist
                if not data.get("hasMore", False):
                    log("✅ Reached end of data (hasMore=false)")
                    break
                    
                offset += limit
                
            except Exception as e:
                log(f"💥 Request Error: {e}")
                break
    
    db.close()
    log(f"🎉 Sync Complete! Total Saved: {total_saved} opportunities")
    return total_saved

if __name__ == "__main__":
    sync_opportunities()
