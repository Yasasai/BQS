
import os
import sys
import httpx
import logging
import asyncio
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", os.getenv("ORACLE_PASS"))
MAX_CONCURRENCY = 5  # Limit concurrent requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def log(msg): 
    print(msg, flush=True)
    logger.info(msg)

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity, Practice

# Minimal Semaphore
sem = asyncio.Semaphore(MAX_CONCURRENCY)

def map_oracle_to_db(item, db: Session):
    """
    Map Oracle JSON to our Opportunity model.
    Using synchronous DB query for Practice lookup inside sync context or pre-cached.
    """
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id: return None
        
        # Parse dates
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
        if item.get("EffectiveDate"):
            try:
                # Often just YYYY-MM-DD
                close_date = datetime.strptime(item["EffectiveDate"][:10], "%Y-%m-%d")
            except: pass

        # Practice lookup/create (synchronous)
        primary_practice_id = None
        practice_val = item.get("Practice_c")
        if practice_val:
            # Check cache or query? Query for safety in sync logic
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
            "is_active": True,
            "local_last_synced_at": datetime.now(timezone.utc)
        }
    except Exception as e:
        log(f"⚠️ Mapping Error for {item.get('OptyId')}: {e}")
        return None

async def fetch_page(client: httpx.AsyncClient, offset: int, limit: int) -> List[dict]:
    """Fetch a single page of opportunities asynchronously."""
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    params = {
        "q": "StatusCode='OPEN'",
        "offset": offset,
        "limit": limit,
        "totalResults": "false", # Optimization: don't calc total on every page
        "fields": "OptyId,OptyNumber,Name,TargetPartyName,Revenue,CurrencyCode,SalesStage,EffectiveDate,LastUpdateDate,OptyLastUpdateDate,Practice_c,GEO_c"
    }

    async with sem:
        try:
            log(f"📡 Fetching offset {offset}...")
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            log(f"✅ Received {len(items)} items from offset {offset}")
            return items
        except Exception as e:
            log(f"❌ Error fetching offset {offset}: {e}")
            return []

async def fetch_total_count(client: httpx.AsyncClient) -> int:
    """Get the total count of opportunities to sync."""
    endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
    params = {
        "q": "StatusCode='OPEN'",
        "totalResults": "true",
        "limit": 1,
        "fields": "OptyId"
    }
    try:
        log("🔄 Checking total count...")
        resp = await client.get(endpoint, params=params)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("totalResults", -1)
            # If explicit totalResults not returned (sometimes happens), assume -1
            if total == -1:
                 # Fallback: check hasMore
                 log("⚠️ 'totalResults' missing, defaulting to paginated discovery.")
                 return -1 
            return int(total)
        else:
            log(f"⚠️ Failed to get count: {resp.status_code}")
            return -1
    except Exception as e:
        log(f"⚠️ Count check failed: {e}")
        return -1

def save_batch_to_db(items: List[dict]):
    """Save a batch of items to the database synchronously."""
    if not items: return 0
    
    init_db()
    db = SessionLocal()
    saved = 0
    try:
        # Pre-cache practices to avoid repeated queries (Optimization)
        # Using a simplistic approach: fetch all names in batch?
        # Or just let map_oracle_to_db handle it one by one (db session cache helps).
        pass 

        for item in items:
            mapped = map_oracle_to_db(item, db)
            if not mapped: continue

            try:
                existing = db.query(Opportunity).filter(
                    Opportunity.opp_id == mapped["opp_id"]
                ).first()
                
                if existing:
                    for k, v in mapped.items():
                        setattr(existing, k, v)
                else:
                    db.add(Opportunity(**mapped))
                
                saved += 1
            except Exception as e:
                log(f"⚠️ DB Save Error: {e}")

        db.commit()
    except Exception as e:
        db.rollback()
        log(f"💥 Critical Batch Save Error: {e}")
    finally:
        db.close()
    
    return saved

async def sync_opportunities_async():
    """Main async sync function with parallel fetching."""
    log("🚀 Starting ASYNC Dynamic Sync...")
    limit = 50
    total_processed = 0
    
    async with httpx.AsyncClient(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        # 1. Get Total Count
        total_count = await fetch_total_count(client)
        
        if total_count > 0:
            log(f"📊 Total records found: {total_count}")
            # Generate tasks
            tasks = []
            for offset in range(0, total_count, limit):
                tasks.append(fetch_page(client, offset, limit))
            
            # Execute in parallel
            log(f"⚡ Launching {len(tasks)} parallel requests...")
            results = await asyncio.gather(*tasks)
            
            # Flatten results
            all_items = [item for page in results for item in page]
            log(f"📥 Downloaded {len(all_items)} records. Saving to DB...")
            
            # Save to DB (Synchronous operation)
            count = save_batch_to_db(all_items)
            total_processed = count
            
        else:
            # Fallback for systems not supporting totalResults or if count failed
            log("⚠️ Total count unavailable or 0. Using sequential discovery (semi-parallel chunks).")
            offset = 0
            while True:
                # Fetch a chunk of pages speculatively? 
                # Let's just do sequential-ish chunks
                chunk_size = 5 # 5 parallel requests
                tasks = []
                for i in range(chunk_size):
                    tasks.append(fetch_page(client, offset + (i * limit), limit))
                
                results = await asyncio.gather(*tasks)
                has_items = False
                batch_items = []
                for page in results:
                    if page:
                        has_items = True
                        batch_items.extend(page)
                
                if batch_items:
                    save_batch_to_db(batch_items)
                    total_processed += len(batch_items)
                
                if not has_items or len(batch_items) < (chunk_size * limit):
                    # Stop if we didn't fill the chunk, roughly indicates end
                    # Not perfect but sufficient for MVP fallback
                    break
                
                offset += (limit * chunk_size)

    log(f"🎉 Async Sync Complete! Total Processed: {total_processed}")
    return total_processed

def sync_opportunities():
    """Synchronous wrapper for async sync (for compatibility)."""
    try:
        return asyncio.run(sync_opportunities_async())
    except Exception as e:
        log(f"❌ Sync Failed: {e}")
        return 0

if __name__ == "__main__":
    sync_opportunities()
