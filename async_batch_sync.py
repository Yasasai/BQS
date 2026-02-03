
import asyncio
import os
import sys
import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path setup to include backend modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))
LIMIT = 50
MAX_CONCURRENCY = 5

# Imports from your existing codebase
try:
    from backend.app.core.database import SessionLocal, init_db
    from backend.app.models import Opportunity, Practice, SyncMeta
except ImportError:
    # Fallback if run directly from root
    sys.path.append(os.path.join(BASE_DIR, "backend"))
    from backend.app.core.database import SessionLocal, init_db
    from backend.app.models import Opportunity, Practice, SyncMeta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def log(msg):
    print(msg, flush=True)
    logger.info(msg)

# Semaphore for concurrency control
sem = asyncio.Semaphore(MAX_CONCURRENCY)

def map_oracle_to_db(item, session: Session):
    """
    Map Oracle JSON item to DB dictionary.
    Reusing logic from sync_manager but adapted for direct dict usage.
    """
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id: return None
        
        # Parse dates
        last_update_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
        crm_last_updated_at = datetime.now(timezone.utc)
        if last_update_str:
            try:
                # Truncate fractional seconds if needed
                crm_last_updated_at = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            except: pass
            
        close_date = None
        if item.get("EffectiveDate"):
            try:
                close_date = datetime.strptime(item["EffectiveDate"][:10], "%Y-%m-%d")
            except: pass

        # Practice logic
        practice_val = item.get("Practice_c")
       
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
            "local_last_synced_at": datetime.now(timezone.utc),
            "practice_name_temp": practice_val, # Temporary holder
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Mapping Error: {e}")
        return None

async def fetch_page(client, offset):
    """
    Fetch a single page of opportunities using explicit StatusCode='OPEN' query.
    """
    async with sem:
        # STRICT QUERY AS REQUESTED
        query = "StatusCode='OPEN'"
        
        params = {
            "q": query,
            "offset": offset,
            "limit": LIMIT,
            "totalResults": "true"
        }
        
        url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
        
        log(f"📡 Fetching offset {offset}...")
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        except Exception as e:
            log(f"❌ Error fetching offset {offset}: {e}")
            return []

async def get_total_count(client):
    """
    Get total count using strict query StatusCode='OPEN'
    """
    # STRICT QUERY AS REQUESTED
    query = "StatusCode='OPEN'"

    params = {
        "q": query,
        "limit": 1,
        "totalResults": "true",
        "fields": "OptyId" 
    }
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    
    log(f"🔍 Getting total count with query: {query}")
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("totalResults", 0)

def bulk_upsert(items):
    """
    Synchronous bulk upsert function.
    """
    if not items: return 0
    
    init_db()
    db = SessionLocal()
    saved_count = 0
    
    try:
        # 1. Pre-process Practices
        practice_names = set(i["practice_name_temp"] for i in items if i["practice_name_temp"])
        
        # Bulk fetch existing
        existing_practices = db.query(Practice).filter(Practice.practice_name.in_(practice_names)).all()
        practice_map = {p.practice_name: p.practice_id for p in existing_practices}
        
        # Create missing
        for pname in practice_names:
            if pname not in practice_map:
                import uuid
                new_p = Practice(
                    practice_id=str(uuid.uuid4()),
                    practice_code=pname.upper().replace(" ", "_")[:20],
                    practice_name=pname
                )
                db.add(new_p)
                db.flush() 
                practice_map[pname] = new_p.practice_id
        
        # 2. Process Opportunities
        for item in items:
            p_val = item.pop("practice_name_temp")
            if p_val:
                item["primary_practice_id"] = practice_map.get(p_val)
            
            # Upsert Logic
            existing_opp = db.query(Opportunity).filter(Opportunity.opp_id == item["opp_id"]).first()
            if existing_opp:
                for k, v in item.items():
                    setattr(existing_opp, k, v)
            else:
                db.add(Opportunity(**item))
            
            saved_count += 1
            
        db.commit()
        log(f"💾 Bulk saved {saved_count} records.")
        
        # Update SyncMeta
        try:
            meta = db.query(SyncMeta).filter(SyncMeta.meta_key == "async_oracle_opties").first()
            if not meta:
                meta = SyncMeta(meta_key="async_oracle_opties")
                db.add(meta)
            meta.last_sync_timestamp = datetime.now(timezone.utc)
            meta.sync_status = "SUCCESS"
            meta.records_processed = saved_count
            db.commit()
        except: pass
        
    except Exception as e:
        log(f"🔥 Bulk Upsert Error: {e}")
        db.rollback()
    finally:
        db.close()
        
    return saved_count

async def main():
    start_time = datetime.now(timezone.utc)
    
    async with httpx.AsyncClient(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        # 2. Get Total Results (Strict query)
        total = await get_total_count(client)
        log(f"📊 Total Records to Sync: {total}")
        
        if total == 0:
            log("✅ Nothing to sync.")
            return

        # 3. Generate Offsets
        offsets = range(0, total, LIMIT)
        
        # 4. Create Tasks
        log(f"🚀 Starting parallel fetch with max concurrency {MAX_CONCURRENCY}...")
        tasks = [fetch_page(client, o) for o in offsets]
        
        # 5. Run!
        pages = await asyncio.gather(*tasks)
        
        # 6. Flatten Results
        raw_items = [item for page in pages for item in page]
        log(f"✅ Fetched {len(raw_items)} items total.")
        
        # 7. Map & Transform
        mapped_items = []
        for item in raw_items:
            mapped = map_oracle_to_db(item, None) 
            if mapped:
                mapped_items.append(mapped)
                
        # 8. Bulk Upsert
        log("💾 Starting bulk upsert...")
        bulk_upsert(mapped_items)

    log(f"🎉 Sync Finished in {(datetime.now(timezone.utc) - start_time).total_seconds():.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
