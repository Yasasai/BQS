import asyncio
import os
import sys
import httpx
import logging
import uuid
import traceback
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path setup 
# Ensuring backend package is discoverable
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.services.oracle_service import ORACLE_USER, ORACLE_PASS, ORACLE_BASE_URL
from backend.app.core.database import SessionLocal
from backend.app.models import (
    CRMOpportunity, CRMOpportunityResource, CRMSyncRun, 
    CRMSyncWatermark, CRMSyncError, CRMSalesRep
)
from backend.app.core.logging_config import setup_logging, get_logger

# Set up standardized logging
setup_logging()
logger = get_logger("async_sync")

LIMIT = 50

# API Endpoints with specific versions as per Task
OPPORTUNITY_API_URL = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities"
SALESREP_API_URL = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.13.18.05/salesreps"
# Opportunity Resource uses 'latest' as per Task
# Base for resource is usually joined to the opportunity endpoint
RESOURCE_API_VERSION = "latest"

def parse_iso_date(date_str):
    """Safely parse Oracle/ISO date strings."""
    if not date_str: return None
    try:
        # Standard Oracle format: 2024-03-12T10:00:00.000+00:00
        # and fallback for Z (UTC)
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception:
        try:
            # Simple date fallback: 2024-03-12
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except Exception:
            return None

def map_opty_to_db(item):
    """
    Map Oracle JSON response to CRMOpportunity model.
    Task 1: Generate CRM Link and handle nullables.
    """
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id or opty_id == "None":
            return None
        
        # CRM navigation link generation
        crm_link = f"{ORACLE_BASE_URL}/crmUI/faces/FuseOverview?OpportunityId={opty_id}"
        
        return {
            "opty_id": opty_id,
            "opty_number": item.get("OptyNumber"),
            "opportunity_name": item.get("Name"),
            "account_name": item.get("TargetPartyName"),
            "revenue": float(item.get("Revenue")) if item.get("Revenue") is not None else None,
            "currency_code": item.get("CurrencyCode"),
            "sales_stage": item.get("SalesStage"),
            "effective_date": parse_iso_date(item.get("EffectiveDate")),
            "last_update_date": parse_iso_date(item.get("LastUpdateDate")),
            "opty_last_update_date": parse_iso_date(item.get("OptyLastUpdateDate")),
            "practice": item.get("Practice_c"),
            "geo": item.get("GEO_c"),
            "crm_link": crm_link,
            "last_seen_ts": datetime.now(timezone.utc)
        }
    except Exception as e:
        logger.error(f"Mapping Error for OptyId {item.get('OptyId')}: {e}")
        return None

async def log_sync_error(db, run_id, endpoint, error_msg):
    """
    Task 6: Record failed API calls or database errors in crm_sync_error.
    """
    try:
        err = CRMSyncError(
            run_id=run_id,
            api_endpoint=endpoint,
            error_message=str(error_msg),
            stack_trace=traceback.format_exc(),
            created_at=datetime.now(timezone.utc)
        )
        db.add(err)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log sync error: {e}")

async def fetch_resources(client, opty_id, run_id, db):
    """
    Task 2: Opportunity Resource Sync per Opportunity.
    """
    # Using 'latest' as per Task 3 Requirement (though mentioned in Task 2 context)
    url = f"{ORACLE_BASE_URL}/crmRestApi/resources/{RESOURCE_API_VERSION}/opportunities/{opty_id}/child/OpportunityResource"
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        
        inserted_count = 0
        for item in items:
            # Mapping per Task 2
            mapped = {
                "opty_id": opty_id,
                "resource_name": item.get("PartyName"),
                "salesrep_number": item.get("SalesrepNumber"),
                "role_code": item.get("RoleCode"),
                "email": item.get("EmailAddress"),
                "last_seen_ts": datetime.now(timezone.utc),
                "last_synced_run_id": run_id
            }
            
            # Upsert Resource
            # Using email and role_code as a composite identify for a person's role on an opty
            existing = db.query(CRMOpportunityResource).filter(
                CRMOpportunityResource.opty_id == opty_id,
                CRMOpportunityResource.email == mapped["email"],
                CRMOpportunityResource.role_code == mapped["role_code"]
            ).first()
            
            if existing:
                for k, v in mapped.items():
                    setattr(existing, k, v)
            else:
                db.add(CRMOpportunityResource(**mapped))
            inserted_count += 1
        
        return inserted_count
    except Exception as e:
        logger.error(f"Error fetching resources for OptyId {opty_id}: {e}")
        await log_sync_error(db, run_id, url, e)
        return 0

async def fetch_sales_reps(client, run_id, db):
    """
    Task 3: Sales Representative Sync.
    """
    params = {"q": "Status='A'", "fields": "PartyName,EmailAddress,SalesrepNumber"}
    try:
        resp = await client.get(SALESREP_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        
        for item in items:
            mapped = {
                "salesrep_number": item.get("SalesrepNumber"),
                "party_name": item.get("PartyName"),
                "email_address": item.get("EmailAddress"),
                "last_seen_ts": datetime.now(timezone.utc),
                "last_synced_run_id": run_id
            }
            
            existing = db.query(CRMSalesRep).filter(CRMSalesRep.salesrep_number == mapped["salesrep_number"]).first()
            if existing:
                for k, v in mapped.items():
                    setattr(existing, k, v)
            else:
                db.add(CRMSalesRep(**mapped))
        
        db.commit()
        logger.info(f"Sales Reps Processed: {len(items)}")
        return len(items)
    except Exception as e:
        logger.error(f"Error fetching Sales Reps: {e}")
        await log_sync_error(db, run_id, SALESREP_API_URL, e)
        return 0

async def run_async_sync():
    """
    Main orchestration logic.
    """
    setup_logging()
    db = SessionLocal()
    run_id = str(uuid.uuid4())
    
    # Task 4: Sync Run Tracking - Create record
    sync_run = CRMSyncRun(
        sync_run_id=run_id,
        start_time=datetime.now(timezone.utc),
        status="RUNNING",
        total_records_processed=0
    )
    db.add(sync_run)
    db.commit()
    
    logger.info(f"Sync Run Started: {run_id}")
    
    total_fetched = 0
    total_upserted = 0
    total_resources = 0
    
    try:
        async with httpx.AsyncClient(auth=(ORACLE_USER, ORACLE_PASS), timeout=60.0) as client:
            
            # Task 3: Sales Rep Sync
            await fetch_sales_reps(client, run_id, db)
            
            # Task 5: Watermark Tracking - Read offset
            watermark = db.query(CRMSyncWatermark).filter(CRMSyncWatermark.object_name == 'opportunities').first()
            if not watermark:
                watermark = CRMSyncWatermark(object_name='opportunities', last_offset=0)
                db.add(watermark)
                db.commit()
            
            offset = watermark.last_offset
            
            # Task 8: Pagination Strategy
            while True:
                params = {
                    "q": "StatusCode='OPEN'",
                    "offset": offset,
                    "limit": LIMIT,
                    "fields": "OptyId,OptyNumber,Name,TargetPartyName,Revenue,CurrencyCode,SalesStage,EffectiveDate,LastUpdateDate,OptyLastUpdateDate,Practice_c,GEO_c",
                    "totalResults": "false"
                }
                
                # Task 7: Logging API Request
                logger.info(f"API Request: Offset={offset} Limit={LIMIT}")
                
                try:
                    resp = await client.get(OPPORTUNITY_API_URL, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("items", [])
                except Exception as e:
                    logger.error(f"API Call Failed for offset {offset}: {e}")
                    await log_sync_error(db, run_id, OPPORTUNITY_API_URL, e)
                    # For non-fatal errors, we might break if api is down
                    break
                
                if not items:
                    # Task 7: Logging Records Received
                    logger.info(f"Records Received: 0")
                    break
                
                logger.info(f"Records Received: {len(items)}")
                
                batch_upsert_count = 0
                batch_resource_count = 0
                
                for item in items:
                    mapped = map_opty_to_db(item)
                    if not mapped: continue
                    
                    mapped["last_synced_run_id"] = run_id
                    
                    # Task 1: Refactor Opportunity Sync Target
                    existing = db.query(CRMOpportunity).filter(CRMOpportunity.opty_id == mapped["opty_id"]).first()
                    if existing:
                        for k, v in mapped.items():
                            setattr(existing, k, v)
                    else:
                        db.add(CRMOpportunity(**mapped))
                    
                    batch_upsert_count += 1
                    
                    # Task 2: Opportunity Resource Sync
                    res_count = await fetch_resources(client, mapped["opty_id"], run_id, db)
                    batch_resource_count += res_count
                
                # Commit batch
                db.commit()
                
                total_upserted += batch_upsert_count
                total_resources += batch_resource_count
                total_fetched += len(items)
                
                # Task 7: Logging
                logger.info(f"Opportunity Upsert Count: {batch_upsert_count}")
                logger.info(f"Opportunity Resource Records Inserted: {batch_resource_count}")
                
                # Task 5: Watermark Tracking - Update offset
                offset += len(items)
                watermark.last_offset = offset
                watermark.last_successful_sync_time = datetime.now(timezone.utc)
                db.commit()
                
                # Break if we got fewer records than requested (end of data)
                if len(items) < LIMIT:
                    break
            
            sync_run.status = "SUCCESS"
            
    except Exception as e:
        logger.critical(f"Sync failed with fatal error: {e}")
        sync_run.status = "FAILED"
        sync_run.error_message = str(e)
        await log_sync_error(db, run_id, "ORCHESTRATOR_MAIN", e)
    finally:
        # Task 4: Sync Run Tracking - End
        sync_run.end_time = datetime.now(timezone.utc)
        sync_run.total_records_processed = total_upserted
        db.commit()
        db.close()
        logger.info(f"Sync Run Finished. Status: {sync_run.status}. Total Processed: {total_upserted}")

if __name__ == "__main__":
    asyncio.run(run_async_sync())
