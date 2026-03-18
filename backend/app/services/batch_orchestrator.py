import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import (
    CRMSyncRun, 
    CRMSyncWatermark, 
    CRMSyncError, 
    CRMOpportunity
)
from app.services.oracle_extractor import OracleCRMClient
from app.services.sync_transformer import (
    process_opportunities, 
    identify_enrichment_targets, 
    process_resources
)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def run_sync_batch(db_session: Session):
    """
    Main Orchestrator for the Oracle CRM Sync Batch Job.
    Coordinates Stage A through G.
    """
    now = datetime.now(timezone.utc)
    
    # --- Stage A: Start ---
    # 1. Get Watermark
    watermark = db_session.query(CRMSyncWatermark).first()
    if not watermark:
        # Seed watermark if it doesn't exist (e.g., 1 year ago)
        last_successful_ts = now - timedelta(days=365)
        watermark = CRMSyncWatermark(last_successful_ts=last_successful_ts)
        db_session.add(watermark)
        logger.debug("Attempting to commit database transaction (Watermark seed)...")
        db_session.commit()
        logger.debug("Database transaction committed successfully (Watermark seed).")
    else:
        last_successful_ts = watermark.last_successful_ts

    watermark_to_ts = now
    logger.debug(f"Starting sync. Watermark FROM: {last_successful_ts}, TO: {watermark_to_ts}")

    # 2. Create Run Record
    sync_run = CRMSyncRun(
        batch_name=f"CRMSync_{now.strftime('%Y%m%d_%H%M%S')}",
        started_at=now,
        status="RUNNING",
        opportunities_fetched=0,
        resources_fetched=0,
        rows_upserted=0
    )
    db_session.add(sync_run)
    logger.debug("Attempting to commit database transaction (sync_run init)...")
    db_session.commit() # Commit to get sync_run_id and show as RUNNING
    logger.debug("Database transaction committed successfully (sync_run init).")
    
    sync_run_id = sync_run.sync_run_id
    # watermark_to_ts is already set above
    
    client = OracleCRMClient()
    
    try:
        total_opps_fetched = 0
        total_rows_upserted = 0
        
        # --- Stage B & C: Fetch & Upsert Opportunities ---
        logger.info(f"Starting Opportunity Fetch from {last_successful_ts} to {watermark_to_ts}")
        
        try:
            # fetch_opportunities is a generator yielding pages (List[Dict])
            for opp_page in client.fetch_opportunities(last_successful_ts, watermark_to_ts):
                page_count = len(opp_page)
                total_opps_fetched += page_count
                
                # Update run record progress occasionally
                sync_run.opportunities_fetched = total_opps_fetched
                db_session.flush()
                
                # --- Stage C: Upsert ---
                upserted = process_opportunities(db_session, opp_page, sync_run_id)
                total_rows_upserted += upserted
                sync_run.rows_upserted = total_rows_upserted
                db_session.flush()
                
            logger.debug("Attempting to commit database transaction (Opportunities batch complete)...")
            db_session.commit()
            logger.debug("Database transaction committed successfully (Opportunities batch complete).")
            logger.info(f"Finished Stage B/C. Fetched: {total_opps_fetched}, Upserted: {total_rows_upserted}")
            
        except Exception as e:
            logger.error(f"Critical failure during Opportunity extraction: {str(e)}")
            sync_run.status = "FAILED"
            sync_run.error_message = f"Opportunity Extraction Failed: {str(e)}"
            sync_run.ended_at = datetime.now(timezone.utc)
            logger.debug("Attempting to commit database transaction (Opportunity failure)...")
            db_session.commit()
            logger.debug("Database transaction committed successfully (Opportunity failure).")
            return # Stop completely if we can't even get opportunities

        # --- Stage D: Identify Enrichment Targets ---
        # Identify which opportunities need resource data
        enrichment_targets = identify_enrichment_targets(db_session)
        logger.info(f"Stage D: Identified {len(enrichment_targets)} opportunities for resource enrichment")
        
        # --- Stage E & F: Fetch & Upsert Resources (The "Partial Success" loop) ---
        total_resources_fetched = 0
        has_partial_failure = False
        
        for target in enrichment_targets:
            try:
                # Stage E: Fetch Resources
                logger.debug(f"Fetching resources for Opportunity {target.opty_number}")
                resources = client.fetch_opportunity_resources(target.opty_number)
                total_resources_fetched += len(resources)
                
                # Stage F: Upsert Resources
                res_upserted = process_resources(
                    db_session, 
                    target.opty_id, 
                    target.opty_number, 
                    resources, 
                    sync_run_id
                )
                total_rows_upserted += res_upserted
                
                # Housekeeping
                sync_run.resources_fetched = total_resources_fetched
                sync_run.rows_upserted = total_rows_upserted
                db_session.flush()
                
            except Exception as e:
                # Task 3: Handle partial failures
                logger.warning(f"Failed to enrich Resource for Opty {target.opty_number}: {str(e)}")
                has_partial_failure = True
                
                # Mark opportunity as FAILED for enrichment so Stage D picks it up next time
                target.enrichment_status = 'FAILED'
                target.enrichment_error = str(e)
                
                # Log to CRMSyncError table
                error_log = CRMSyncError(
                    sync_run_id=sync_run_id,
                    entity_type="RESOURCE",
                    entity_id=target.opty_id,
                    error_message=str(e)
                )
                db_session.add(error_log)
                db_session.flush()
                
        # Final Commit for Resources
        logger.debug("Attempting to commit database transaction (Resources)...")
        db_session.commit()
        logger.debug("Database transaction committed successfully (Resources).")
        
        # --- Stage G: Close ---
        sync_run.ended_at = datetime.now(timezone.utc)
        
        if has_partial_failure:
            sync_run.status = "PARTIAL_SUCCESS"
        else:
            sync_run.status = "SUCCESS"
            
        # Only advance watermark if not FAILED
        # (Technically, even PARTIAL_SUCCESS means we processed the opportunity list,
        # and individual failures are flagged for retry in Stage D next time)
        watermark.last_successful_ts = watermark_to_ts
        
        logger.debug("Attempting to commit database transaction (Final Stage G)...")
        db_session.commit()
        logger.debug("Database transaction committed successfully (Final Stage G).")
        logger.info(f"Sync Run {sync_run_id} completed with status: {sync_run.status}")
        
    except Exception as e:
        # Catch-all for unexpected global failures
        logger.exception("Global failure in sync orchestrator")
        sync_run.status = "FAILED"
        sync_run.error_message = f"Global Orchestrator Error: {str(e)}"
        sync_run.ended_at = datetime.now(timezone.utc)
        logger.debug("Attempting to commit database transaction (Global failure)...")
        db_session.commit()
        logger.debug("Database transaction committed successfully (Global failure).")

if __name__ == "__main__":
    # For local testing if needed
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        run_sync_batch(db)
    finally:
        db.close()
