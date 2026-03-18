from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx, asyncio
from datetime import datetime, timezone
import logging

from backend.app.core.database import get_db
from backend.app.models import Opportunity

logger = logging.getLogger("oracle_sync")

router = APIRouter(prefix="/api/opportunities", tags=["opportunities-sync"])

from backend.app.services.oracle_service import ORACLE_REST_ROOT
ORACLE_API_URL = f"{ORACLE_REST_ROOT}/opportunities"
PAGE_LIMIT = 50
CONCURRENCY = 5  # Fetch 5 pages at a time

async def fetch_page(client: httpx.AsyncClient, offset: int, last_updated_str: str = None) -> list[dict]:
    q_param = "StatusCode='OPEN'"
    if last_updated_str:
        q_param += f" and LastUpdateDate>'{last_updated_str}'"
    
    params = {
        "q": q_param,
        "offset": offset,
        "limit": PAGE_LIMIT,
        "totalResults": "false",
        "fields": "OptyId,OptyNumber,Name,TargetPartyName,Revenue,CurrencyCode,SalesStage,EffectiveDate,LastUpdateDate,OptyLastUpdateDate,Practice_c,GEO_c",
    }
    
    try:
        resp = await client.get(ORACLE_API_URL, params=params, timeout=60.0)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        elif isinstance(data, list):
            return data
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching offset {offset}: {e}")
        return []

async def upsert_opportunities(db: Session, items: list[dict]):
    if not items:
        return
        
    for item in items:
        try:
            last_update_str = item.get("LastUpdateDate")
            last_update_date = None
            if last_update_str:
                # Oracle format handles correctly
                last_update_str = last_update_str.replace("Z", "+00:00")
                if len(last_update_str) > 19 and last_update_str[19] == '.':
                    last_update_date = datetime.strptime(last_update_str[:19] + last_update_str[-6:], "%Y-%m-%dT%H:%M:%S%z")
                else:
                    last_update_date = datetime.strptime(last_update_str, "%Y-%m-%dT%H:%M:%S%z")
            if not last_update_date:
                last_update_date = datetime.now(timezone.utc)
        except Exception:
            last_update_date = datetime.now(timezone.utc)

        revenue = item.get("Revenue")
        try:
            revenue = float(revenue) if revenue is not None else 0.0
        except ValueError:
            revenue = 0.0

        opp = Opportunity(
            opp_id=item.get("OptyId"),
            opp_number=item.get("OptyNumber"),
            opp_name=item.get("Name"),
            customer_name=item.get("TargetPartyName") or "Unknown Account",
            deal_value=revenue,
            currency=item.get("CurrencyCode"),
            stage=item.get("SalesStage"),
            crm_last_updated_at=last_update_date,
            geo=item.get("GEO_c"),
        )
        db.merge(opp)
        
    # Commit after each batch
    db.commit()

async def sync_all(db: Session):
    # 1. Determine incremental timestamp
    latest_update = db.query(func.max(Opportunity.crm_last_updated_at)).scalar()
    last_updated_str = None
    if latest_update:
        # Format into Oracle acceptable format (e.g. 2023-01-01T00:00:00.000+00:00)
        # Timezone aware datetime to string
        if latest_update.tzinfo is None:
            latest_update = latest_update.replace(tzinfo=timezone.utc)
        last_updated_str = latest_update.strftime("%Y-%m-%dT%H:%M:%S.000%z")
        # Format the offset to insert colon (+00:00 instead of +0000)
        if last_updated_str.endswith("0000") and not last_updated_str.endswith(":00"):
            last_updated_str = last_updated_str[:-2] + ":" + last_updated_str[-2:]
        logger.info(f"Incremental sync: fetching changes after {last_updated_str}")
    else:
        logger.info("Full sync: fetching all open opportunities")

    # 2. Parallel fetching logic
    total_upserted = 0
    async with httpx.AsyncClient() as client:
        offset = 0
        while True:
            # Prepare parallel requests
            tasks = []
            for i in range(CONCURRENCY):
                tasks.append(fetch_page(client, offset + i * PAGE_LIMIT, last_updated_str))
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_items = []
            stop_fetching = False
            
            for page in results:
                if isinstance(page, Exception):
                    logger.error(f"Batch task failed with error: {page}")
                    stop_fetching = True
                    break
                    
                if not page:
                    stop_fetching = True
                    break
                    
                all_items.extend(page)
                
                # If any page returned less than full PAGE_LIMIT, we reached the end
                if len(page) < PAGE_LIMIT:
                    stop_fetching = True
                    # We continue appending to all_items for this batch iteration but will stop looping globally
            
            # Upsert the gathered batch
            if all_items:
                await upsert_opportunities(db, all_items)
                total_upserted += len(all_items)
                
            if stop_fetching:
                break
                
            offset += CONCURRENCY * PAGE_LIMIT

    logger.info(f"Sync complete. Total upserted: {total_upserted}")
    return total_upserted

@router.post("/sync-oracle", response_model=dict)
async def trigger_sync(db: Session = Depends(get_db)):
    try:
        total = await sync_all(db)
        return {"status": "success", "message": f"Oracle opportunities synced incrementally in parallel. Processed {total} records."}
    except Exception as e:
        logger.error(f"Sync trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
