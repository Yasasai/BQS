"""
Oracle CRM to PostgreSQL Sync Manager
Handles full and incremental synchronization with robust error handling
"""
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from database import SessionLocal, Opportunity, OpportunityDetails, OpportunityIDLog, SyncLog
from oracle_service import get_all_opportunities, map_oracle_to_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyncManager:
    """Manages Oracle CRM synchronization with PostgreSQL"""
    
    def __init__(self):
        self.db: Session = None
        self.sync_stats = {
            'total_fetched': 0,
            'new_records': 0,
            'updated_records': 0,
            'failed_records': 0,
            'start_time': None,
            'end_time': None,
            'is_full_sync': False
        }
    
    def get_last_update_date(self) -> str:
        """Query max LastUpdateDate from local DB for incremental sync"""
        try:
            # We use last_synced_at as a fallback, but ideally we'd store Oracle's LastUpdateDate
            result = self.db.execute(
                text("SELECT MAX(last_synced_at) FROM opportunities")
            ).fetchone()
            
            if result and result[0]:
                # Format: YYYY-MM-DDTHH:MM:SS
                return result[0].strftime("%Y-%m-%dT%H:%M:%S")
            return None
        except Exception as e:
            logger.warning(f"Could not retrieve last update date: {e}")
            return None

    def log_change(self, opp_remote_id, field, old_val, new_val, sync_id):
        """Log changes or errors to OpportunityIDLog"""
        if str(old_val) == str(new_val):
            return
            
        log_entry = OpportunityIDLog(
            opp_id=opp_remote_id,
            field_name=field,
            old_value=str(old_val)[:255] if old_val is not None else "NONE",
            new_value=str(new_val)[:255] if new_val is not None else "NONE",
            sync_id=sync_id
        )
        self.db.add(log_entry)

    def sync_batch(self, batch_items, sync_id):
        """Process a batch of opportunities with self-healing Deep Fetch"""
        from oracle_service import fetch_single_opportunity, map_oracle_to_db
        
        for item in batch_items:
            remote_id = str(item.get('OptyNumber') or item.get('OptyId'))
            try:
                mapped_result = map_oracle_to_db(item)
                if not mapped_result:
                    self.log_change(remote_id, "ERROR", "Mapping", "Failed to map JSON", sync_id)
                    self.sync_stats['failed_records'] += 1
                    continue
                
                primary_mapped = mapped_result["primary"]
                details_mapped = mapped_result["details"]
                
                # SELF-HEALING: If critical data is missing, perform a Deep Fetch
                is_incomplete = primary_mapped.get('deal_value') == 0 or primary_mapped.get('practice') == "General"
                if is_incomplete:
                    logger.info(f"🔍 {remote_id} incomplete. Triggering Deep Fetch...")
                    deep_item = fetch_single_opportunity(remote_id)
                    if deep_item:
                        deep_mapped_result = map_oracle_to_db(deep_item)
                        if deep_mapped_result:
                            primary_mapped = deep_mapped_result["primary"]
                            details_mapped = deep_mapped_result["details"]
                
                # 1. Sync Primary Opportunity Table
                existing = self.db.query(Opportunity).filter(Opportunity.remote_id == remote_id).first()
                if existing:
                    # Log field changes
                    for field in ['deal_value', 'win_probability', 'stage', 'practice', 'geo', 'sector']:
                        self.log_change(remote_id, field, getattr(existing, field), primary_mapped[field], sync_id)
                    
                    # Update fields
                    for key, val in primary_mapped.items():
                        setattr(existing, key, val)
                    
                    # Close mapping
                    oracle_stage = primary_mapped.get('stage', '').upper()
                    if any(x in oracle_stage for x in ['CLOSED', 'WON', 'LOST']):
                        existing.workflow_status = 'CLOSED_IN_CRM'
                        existing.status = 'CLOSED_IN_CRM'
                        
                    self.sync_stats['updated_records'] += 1
                else:
                    new_opp = Opportunity(
                        **primary_mapped,
                        workflow_status='NEW',
                        status='New from CRM'
                    )
                    self.db.add(new_opp)
                    self.sync_stats['new_records'] += 1
                
                # 2. Sync Opportunity Details Table
                existing_details = self.db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == remote_id).first()
                if existing_details:
                    for key, val in details_mapped.items():
                        setattr(existing_details, key, val)
                else:
                    new_details = OpportunityDetails(**details_mapped)
                    self.db.add(new_details)
                
            except Exception as e:
                logger.error(f"❌ Error syncing {remote_id}: {e}")
                self.log_change(remote_id, "CRITICAL_ERROR", "Exception", str(e), sync_id)
                self.sync_stats['failed_records'] += 1
        
        self.db.commit()

    def perform_sync(self, force_full=False):
        """
        Automated Sync Orchestration
        A. Determine Sync Mode
        B. Fetch Data from Oracle (Generator)
        C. Process Each Batch
        D. Logging
        """
        self.db = SessionLocal()
        self.sync_stats['start_time'] = datetime.utcnow()
        
        # A. Determine Sync Mode
        since_date = None
        if not force_full:
            since_date = self.get_last_update_date()
        
        self.sync_stats['is_full_sync'] = since_date is None
        sync_type = 'FULL' if self.sync_stats['is_full_sync'] else 'INCREMENTAL'
        
        # Initialize Sync Log
        sync_log = SyncLog(
            sync_type=sync_type,
            status='RUNNING',
            started_at=self.sync_stats['start_time']
        )
        self.db.add(sync_log)
        self.db.commit()
        self.db.refresh(sync_log)
        
        try:
            # B. Fetch Data from Oracle (Generator)
            items_gen = get_all_opportunities(batch_size=10, since_date=since_date)
            
            # C. Process Each Batch
            for batch in items_gen:
                if batch and self.sync_stats['total_fetched'] == 0:
                    print(f"DEBUG: First record keys: {list(batch[0].keys())[:15]}")
                
                self.sync_stats['total_fetched'] += len(batch)
                self.sync_batch(batch, sync_log.id)
                logger.info(f"Saved {self.sync_stats['total_fetched']} records...")
            
            # D. Final Logging
            self.sync_stats['end_time'] = datetime.utcnow()
            duration = (self.sync_stats['end_time'] - self.sync_stats['start_time']).total_seconds()
            
            # Special case: 0 records found is often a permissions issue
            if self.sync_stats['total_fetched'] == 0:
                sync_log.status = 'FAILED'
                sync_log.error_message = "Zero records found. This usually indicates a permissions issue or that 'RecordSet=ALL' is required for your user account."
            else:
                sync_log.status = 'SUCCESS'
            
            sync_log.total_fetched = self.sync_stats['total_fetched']
            sync_log.new_records = self.sync_stats['new_records']
            sync_log.updated_records = self.sync_stats['updated_records']
            sync_log.failed_records = self.sync_stats['failed_records']
            sync_log.completed_at = self.sync_stats['end_time']
            sync_log.duration_seconds = int(duration)
            
            self.db.commit()
            logger.info(f"✅ Sync completed: {self.sync_stats['total_fetched']} records processed.")
            return self.sync_stats
            
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            sync_log.status = 'FAILED'
            sync_log.error_message = str(e)
            self.db.commit()
            raise
        finally:
            self.db.close()

def sync_opportunities(force=False):
    """Entry point for sync process with retry logic for broken pipes"""
    import time
    
    max_retries = 3
    retry_delay = 5 # seconds
    
    for attempt in range(max_retries):
        try:
            manager = SyncManager()
            return manager.perform_sync(force_full=force)
        except (OperationalError, Exception) as e:
            error_str = str(e)
            is_broken_pipe = "broken pipe" in error_str.lower() or "233" in error_str
            
            if is_broken_pipe and attempt < max_retries - 1:
                logger.warning(f"⚠️  Database pipe broken (Attempt {attempt+1}/{max_retries}). Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"❌ Sync failed permanently: {e}")
                raise

if __name__ == "__main__":
    sync_opportunities()
