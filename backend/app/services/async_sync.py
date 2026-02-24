
import asyncio
import os
import sys
import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path setup to include backend modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# sys.path.append(BASE_DIR) 

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuration
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))
LIMIT = 50
MAX_CONCURRENCY = 3 # Reduced to prevent overwhelmed DB

# Imports
from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity, Practice, SyncMeta


# Set up file logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "async_sync.log")
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def log(msg):
    logger.info(msg)

# Semaphore for concurrency control
sem = asyncio.Semaphore(MAX_CONCURRENCY)

# EXPICIT FIELDS TO FETCH (Fixes Rank 3: Field Visibility)
# Verified Fields from User Feedback/Docs
# Note: User mentioned 'StatusCd' vs 'StatusCode' - standard is usually StatusCd or OptyStatusCd.
# We will use 'StatusCd' if possible but fallback logic isn't possible in 'fields' param.
# We will remove risky fields from the request list and rely on standard ones first.
FETCH_FIELDS = [
    "OptyId", "OptyNumber", "Name", "TargetPartyName", 
    "Revenue", "CurrencyCode", "SalesStage", "EffectiveDate", 
    "LastUpdateDate", "OptyLastUpdateDate", 
    "Practice_c", "GEO_c" # Assuming these are custom, will check describe later
]
FIELDS_PARAM = ",".join(FETCH_FIELDS)

QUERY_FILTER = "StatusCode='OPEN'" # user indicated 'StatusCd' failed, 'StatusCode' is standard

def map_oracle_to_db(item, session: Session):
    """
    Map Oracle JSON item to DB dictionary.
    Handles strict mapping and potential missing keys.
    """
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id: return None
        
        # Parse dates with robust fallback
        last_update_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
        crm_last_updated_at = datetime.now(timezone.utc)
        if last_update_str:
            try:
                if last_update_str.endswith('Z'):
                    crm_last_updated_at = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
                else:
                    crm_last_updated_at = datetime.fromisoformat(last_update_str)
            except: pass
            
        close_date = None
        eff_date = item.get("EffectiveDate")
        if eff_date:
            try:
                close_date = datetime.strptime(eff_date[:10], "%Y-%m-%d")
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
            "practice_name_temp": practice_val, 
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Mapping Error for item {item.get('OptyId')}: {e}")
        return None

async def fetch_page(client, offset):
    """
    Fetch a single page of opportunities using explicit FIELDS and filter.
    NO totalResults=true here (Rank 1 fix).
    """
    async with sem:
        params = {
            "q": QUERY_FILTER,
            "offset": offset,
            "limit": LIMIT,
            "fields": FIELDS_PARAM 
        }
        
        url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
        
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        except Exception as e:
            log(f"Error fetching offset {offset}: {e}")
            # Try debugging response
            if hasattr(e, 'response'):
                log(f"Response: {e.response.text}")
            return []

async def get_total_count(client):
    """
    Get total count using ONLY q and totalResults=true.
    NO limit, NO fields (Rank 1 fix).
    """
    params = {
        "q": QUERY_FILTER,
        "totalResults": "true" 
        # Intentionally omitting limit and fields to avoid conflicts
    }
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    
    log(f"Getting total count with query: {QUERY_FILTER}")
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("totalResults", 0)
    except Exception as e:
        log(f"Error fetching count: {e}")
        if hasattr(e, 'response'):
             log(f"Response: {e.response.text}")
        return 0

def bulk_upsert(items):
    """
    Synchronous bulk upsert function.
    """
    if not items: return 0
    
    db = SessionLocal()
    saved_count = 0
    
    try:
        # 1. Pre-process Practices
        practice_names = set(i["practice_name_temp"] for i in items if i["practice_name_temp"])
        
        if practice_names:
            existing_practices = db.query(Practice).filter(Practice.practice_name.in_(practice_names)).all()
            practice_map = {p.practice_name: p.practice_id for p in existing_practices}
            
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
        else:
            practice_map = {}
        
        # 2. Process Opportunities
        for item in items:
            p_val = item.pop("practice_name_temp")
            if p_val:
                item["primary_practice_id"] = practice_map.get(p_val)
            
            existing = db.query(Opportunity).filter(Opportunity.opp_id == item["opp_id"]).first()
            if existing:
                for k, v in item.items():
                    setattr(existing, k, v)
            else:
                db.add(Opportunity(**item))
            
            saved_count += 1
            
        db.commit()
        log(f"Bulk saved {saved_count} records.")
        
    except Exception as e:
        log(f"Bulk Upsert Error: {e}")
        db.rollback()
    finally:
        db.close()
        
    return saved_count

async def run_async_sync():
    """
    Main entry point for async sync.
    """
    start_time = datetime.now(timezone.utc)
    log("Starting Safe Async Sync (v2)...")
    
    total_processed = 0
    
    async with httpx.AsyncClient(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        # 2. Get Total Results (Strict query)
        total = await get_total_count(client)
        log(f"Total Records to Sync: {total}")
        
        if total == 0:
            log("Nothing to sync or failed to get count.")
            return

        # 3. Process in Visual Batches
        offsets = range(0, total, LIMIT)
        TASK_CHUNK_SIZE = 5 # Small concurrency
        
        offset_list = list(offsets)
        for i in range(0, len(offset_list), TASK_CHUNK_SIZE):
            chunk_offsets = offset_list[i : i + TASK_CHUNK_SIZE]
            log(f"Processing chunk {i//TASK_CHUNK_SIZE + 1} / {len(offset_list)//TASK_CHUNK_SIZE + 1} (Offsets {chunk_offsets[0]}-{chunk_offsets[-1]})")
            
            tasks = [fetch_page(client, o) for o in chunk_offsets]
            pages = await asyncio.gather(*tasks)
            
            chunk_items = [item for page in pages for item in page]
            
            if chunk_items:
                mapped = []
                for item in chunk_items:
                    m = map_oracle_to_db(item, None)
                    if m: mapped.append(m)
                
                if mapped:
                    bulk_upsert(mapped)
                    total_processed += len(mapped)

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    log(f"Sync Finished in {duration:.2f}s. Total Processed: {total_processed}")
    return {"status": "success", "total": total_processed, "duration": duration}

if __name__ == "__main__":
    asyncio.run(run_async_sync())
