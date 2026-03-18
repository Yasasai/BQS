"""
Oracle CRM Batch Sync with Offset Tracking
===========================================

This is a SEPARATE sync implementation that:
1. Tracks offset in database
2. Supports resumable sync
3. Uses batch processing
4. Minimal field selection for performance

DO NOT mix with existing sync_manager.py
This is an ADDITIONAL option for syncing.
"""

import os
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment
load_dotenv()

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_API_VERSION = os.getenv("ORACLE_API_VERSION", "11.12.1.0")
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Create separate base for this module
Base = declarative_base()

# ============================================================================
# MODEL: Sync State (Tracks offset)
# ============================================================================

class SyncMeta(Base):
    """Tracks the current sync offset for resumable sync"""
    __tablename__ = "sync_offset_meta"
    
    id = Column(Integer, primary_key=True)
    sync_name = Column(String, unique=True, nullable=False)  # e.g., "oracle_opportunities"
    current_offset = Column(Integer, default=0)
    total_synced = Column(Integer, default=0)
    last_sync_at = Column(DateTime, nullable=True)
    is_complete = Column(Integer, default=0)  # 0 = in progress, 1 = complete


# ============================================================================
# MODEL: Minimal Opportunity (Just ID and Number)
# ============================================================================

class OracleOpportunity(Base):
    """Stores minimal opportunity data (ID and Number only) in staging table"""
    __tablename__ = "oracle_opportunities_offset"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opty_id = Column(String, unique=True, nullable=False)
    opty_number = Column(String, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_batch_sync_db():
    """Initialize database tables for batch sync"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    logger.info("✅ Batch sync tables created/verified")
    return sessionmaker(bind=engine)


# ============================================================================
# OFFSET MANAGEMENT
# ============================================================================

def get_offset_from_db(db: Session, sync_name: str = "oracle_opportunities") -> int:
    """Get current offset from database"""
    state = db.query(SyncMeta).filter(SyncMeta.sync_name == sync_name).first()
    
    if not state:
        # First time - create new state
        state = SyncMeta(
            sync_name=sync_name,
            current_offset=0,
            total_synced=0,
            is_complete=0
        )
        db.add(state)
        db.commit()
        logger.info(f"📝 Created new sync state for '{sync_name}'")
        return 0
    
    logger.warning(f"Resetting sync tracking. Forcing new Oracle API call...")
    if state.is_complete:
        logger.info(f"✅ Sync '{sync_name}' already complete. Resetting to 0.")
        state.current_offset = 0
        state.is_complete = 0
        db.commit()
        return 0
    
    logger.info(f"📍 Resuming from offset: {state.current_offset}")
    return state.current_offset


def update_offset_in_db(db: Session, offset: int, synced_count: int, 
                        sync_name: str = "oracle_opportunities", 
                        is_complete: bool = False):
    """Update offset in database"""
    state = db.query(SyncMeta).filter(SyncMeta.sync_name == sync_name).first()
    
    if state:
        state.current_offset = offset
        state.total_synced = synced_count
        state.last_sync_at = datetime.utcnow()
        state.is_complete = 1 if is_complete else 0
        db.commit()
        logger.info(f"💾 Updated offset to {offset}, total synced: {synced_count}")


# ============================================================================
# URL BUILDER
# ============================================================================

def build_url(batch_size: int, offset: int) -> str:
    """
    Build Oracle API URL with batch size and offset
    
    Exact URL format:
    https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
    ?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
    &fields=OptyId,OptyNumber
    &limit=5
    &offset=0
    """
    base_url = f"{ORACLE_BASE_URL}/crmRestApi/resources/{ORACLE_API_VERSION}/opportunities"
    
    # Build query parameters - Correct Oracle field names
    params = {
        "finder": "MyOpportunitiesFinder;RecordSet='ALLOPTIES'",
        "fields": "OptyId,OptyNumber",  # <--- Correct Oracle Field Names
        "limit": batch_size,
        "offset": offset
    }
    
    # Convert to query string
    query_parts = []
    for key, value in params.items():
        query_parts.append(f"{key}={value}")
    
    query_string = "&".join(query_parts)
    full_url = f"{base_url}?{query_string}"
    
    logger.info(f"🔗 Built URL: {full_url}")
    
    return full_url


# ============================================================================
# API CALLER
# ============================================================================

def call_api(url: str) -> dict:
    """Call Oracle API and return response"""
    logger.info(f"📡 Calling Oracle API (GET): {url[:150]}...")
    
    logger.info(f"STAGE 3: Making HTTP GET to: {url} with params: None")
    with httpx.Client(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
        response = client.get(url)
        
        logger.info(f"STAGE 4: Received HTTP {response.status_code} from Oracle.")
        if response.status_code != 200:
            logger.error(f"❌ API Error: {response.status_code} - {response.text[:200]}")
            raise Exception(f"API Error: {response.status_code}")
        
        data = response.json()
        logger.info(f"✅ Received {len(data.get('items', []))} items")
        return data


# ============================================================================
# SAVE TO DB
# ============================================================================

def save_to_db(db: Session, opty_id: str, opty_number: str):
    """Save opportunity ID and Number to database"""
    try:
        # Check if exists
        result = db.query(OracleOpportunity).filter(
            OracleOpportunity.opty_id == opty_id
        ).all()
        existing = result[0] if result else None
        
        if existing:
            # Update
            existing.opty_number = opty_number
            existing.synced_at = datetime.utcnow()
            logger.info(f"   🔄 Updated: {opty_id} - {opty_number}")
        else:
            # Insert
            new_opp = OracleOpportunity(
                opty_id=opty_id,
                opty_number=opty_number
            )
            db.add(new_opp)
            logger.info(f"   ✅ Saved: {opty_id} - {opty_number}")
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"   ❌ Error saving {opty_id}: {e}")
        return False


# ============================================================================
# MAIN BATCH SYNC FUNCTION
# ============================================================================

def batch_sync_opportunities(batch_size: int = 5, sync_name: str = "oracle_opportunities", force_reset: bool = False):
    """
    Main batch sync function following the pseudocode
    
    Args:
        batch_size: Number of records to fetch per batch (default: 5)
        sync_name: Name of this sync job (for tracking)
        force_reset: Whether to reset the offset to 0 before starting
    """
    logger.info("=" * 70)
    logger.info("🚀 Starting Batch Sync with Offset Tracking")
    logger.info("STAGE 2: Entering Oracle API extractor function.")
    logger.info("=" * 70)
    
    # Initialize database
    SessionLocal = init_batch_sync_db()
    
    # Get offset from DB using a short-lived session
    db_init = SessionLocal()
    try:
        if force_reset:
            logger.warning(f"🔄 Forced sync requested. Resetting state for '{sync_name}'...")
            reset_sync(sync_name)
        
        offset = get_offset_from_db(db_init, sync_name)
    finally:
        db_init.close()
    
    total_synced = 0
    
    try:
        # Main sync loop
        while True:
            logger.info(f"\n{'='*70}")
            logger.info(f"📦 Batch: Offset={offset}, Size={batch_size}")
            logger.info(f"{'='*70}")
            
            # Build URL
            url = build_url(batch_size, offset)
            
            # Explicit log after offset check (as requested)
            logger.info(f"🚀 Offset retrieved: {offset}. Bypassing check and initiating Oracle API fetch via HTTP/GET...")
            
            # ── Per-batch clean session ──────────────────────────────────────
            db = SessionLocal()
            try:
                # Call API
                try:
                    response = call_api(url)
                except Exception as e:
                    logger.error(f"💥 API call failed: {e}")
                    break
                
                # Get items
                items = response.get("items", [])
                
                if not items:
                    logger.info("✅ No more items found. Sync complete!")
                    update_offset_in_db(db, offset, total_synced, sync_name, is_complete=True)
                    break
                
                # Process each item
                logger.info(f"📝 Processing {len(items)} items...")
                batch_saved = 0
                
                for item in items:
                    opty_id = str(item.get("OptyId", ""))  # <--- Correct Oracle field name
                    opty_number = str(item.get("OptyNumber", ""))  # <--- Correct Oracle field name
                    
                    if opty_id:
                        if save_to_db(db, opty_id, opty_number):
                            batch_saved += 1
                
                total_synced += batch_saved
                logger.info(f"✅ Batch complete: {batch_saved}/{len(items)} saved")
                
                # Update offset
                offset = offset + batch_size
                update_offset_in_db(db, offset, total_synced, sync_name, is_complete=False)
                
                # Check if more data exists
                has_more = response.get("hasMore", False)
                if not has_more:
                    logger.info("✅ No more data (hasMore=false). Sync complete!")
                    update_offset_in_db(db, offset, total_synced, sync_name, is_complete=True)
                    break
            except Exception as _batch_err:
                db.rollback()
                logger.error(f"💥 Batch error (rolled back): {_batch_err}")
                raise
            finally:
                db.close()
            # ── end per-batch session ─────────────────────────────────────────
        
        logger.info("\n" + "=" * 70)
        logger.info(f"🎉 Sync Complete!")
        logger.info(f"STAGE 5 SUCCESS: Extracted and passed records to database logic.")
        logger.info(f"   Total Synced: {total_synced}")
        logger.info(f"   Final Offset: {offset}")
        logger.info("=" * 70)
        
        return total_synced
        
    except Exception as e:
        logger.error(f"💥 Sync Error: {e}")
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def reset_sync(sync_name: str = "oracle_opportunities"):
    """Reset sync state to start from beginning"""
    SessionLocal = init_batch_sync_db()
    db = SessionLocal()
    
    try:
        state = db.query(SyncMeta).filter(SyncMeta.sync_name == sync_name).first()
        if state:
            state.current_offset = 0
            state.total_synced = 0
            state.is_complete = 0
            state.last_sync_at = None
            db.commit()
            logger.info(f"🔄 Reset sync state for '{sync_name}'")
        else:
            logger.info(f"ℹ️  No sync state found for '{sync_name}'")
    finally:
        db.close()


def get_sync_status(sync_name: str = "oracle_opportunities"):
    """Get current sync status"""
    SessionLocal = init_batch_sync_db()
    db = SessionLocal()
    
    try:
        state = db.query(SyncMeta).filter(SyncMeta.sync_name == sync_name).first()
        
        if not state:
            logger.info(f"ℹ️  No sync state found for '{sync_name}'")
            return None
        
        status = {
            "sync_name": state.sync_name,
            "current_offset": state.current_offset,
            "total_synced": state.total_synced,
            "last_sync_at": state.last_sync_at,
            "is_complete": bool(state.is_complete)
        }
        
        logger.info(f"\n📊 Sync Status for '{sync_name}':")
        logger.info(f"   Offset: {status['current_offset']}")
        logger.info(f"   Total Synced: {status['total_synced']}")
        logger.info(f"   Last Sync: {status['last_sync_at']}")
        logger.info(f"   Complete: {status['is_complete']}")
        
        return status
        
    finally:
        db.close()


def get_synced_count():
    """Get count of synced opportunities"""
    SessionLocal = init_batch_sync_db()
    db = SessionLocal()
    
    try:
        count = db.query(OracleOpportunity).count()
        logger.info(f"📊 Total opportunities in oracle_opportunities table: {count}")
        return count
    finally:
        db.close()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            # Run sync with optional batch size
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            batch_sync_opportunities(batch_size=batch_size)
        
        elif command == "status":
            # Show sync status
            get_sync_status()
            get_synced_count()
        
        elif command == "reset":
            # Reset sync state
            reset_sync()
        
        else:
            print("Unknown command. Use: sync, status, or reset")
    
    else:
        # Default: run sync with batch size 5
        batch_sync_opportunities(batch_size=5)
