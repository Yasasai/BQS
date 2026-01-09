from sqlalchemy.orm import Session
from database import SessionLocal, Opportunity
from oracle_service import get_oracle_opportunities, map_oracle_to_db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def sync_opportunities(db: Session = None):
    """
    Orchestrate the sync: Fetch from Oracle -> Upsert to DB.
    If db is provided, uses it. If not, creates a new session and closes it after.
    """
    logger.info("Starting Opportunity Sync...")
    
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    try:
        oracle_items = get_oracle_opportunities()
        
        synced_count = 0
        
        for item in oracle_items:
            try:
                mapped_data = map_oracle_to_db(item)
                
                # Check if exists
                remote_id = mapped_data["remote_id"]
                existing_opp = db.query(Opportunity).filter(Opportunity.remote_id == remote_id).first()
                
                if existing_opp:
                    # Update fields
                    for key, value in mapped_data.items():
                        setattr(existing_opp, key, value)
                    existing_opp.last_synced_at = datetime.utcnow()
                else:
                    # Create new
                    new_opp = Opportunity(**mapped_data)
                    db.add(new_opp)
                
                synced_count += 1
            except Exception as e:
                logger.error(f"Error syncing item {item.get('OptyId')}: {e}")
                continue
        
        db.commit()
        logger.info(f"Sync complete. Processed {synced_count} items.")
        return {"status": "success", "count": synced_count}

    except Exception as e:
        db.rollback()
        logger.error(f"Database commit error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if should_close:
            db.close()


