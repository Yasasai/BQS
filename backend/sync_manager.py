from sqlalchemy.orm import Session
from database import SessionLocal, Opportunity
from oracle_service import get_oracle_opportunities, map_oracle_to_db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def sync_opportunities(db: Session = None):
    """
    Orchestrate the sync: Fetch from Oracle -> Upsert to DB.
    Uses frequent commits to ensure 'spontaneous saving' and minimize data loss.
    """
    logger.info("Starting Opportunity Sync...")
    
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    metrics = {"total": 0, "updated": 0, "created": 0, "errors": 0}

    try:
        oracle_items = get_oracle_opportunities()
        metrics["total"] = len(oracle_items)
        
        for index, item in enumerate(oracle_items):
            try:
                mapped_data = map_oracle_to_db(item)
                
                if not mapped_data:
                    metrics["errors"] += 1
                    continue

                remote_id = mapped_data.get("remote_id")
                if not remote_id:
                    logger.warning(f"Skipping item without unique ID: {item}")
                    metrics["errors"] += 1
                    continue

                # Check if exists
                existing_opp = db.query(Opportunity).filter(Opportunity.remote_id == remote_id).first()
                
                if existing_opp:
                    # Update fields - only update if changed? 
                    # For now, we update to ensure latest Oracle state is reflected.
                    # We preserving workflow_status if needed, but updating CRM fields.
                    changed = False
                    for key, value in mapped_data.items():
                        # Don't overwrite some local fields if logic dictates (e.g. status)
                        # But user wants "Fetch all data". 
                        # We generally trust Oracle as source of truth for these fields.
                        if getattr(existing_opp, key) != value:
                            setattr(existing_opp, key, value)
                            changed = True
                    
                    if changed:
                        existing_opp.last_synced_at = datetime.utcnow()
                        metrics["updated"] += 1
                else:
                    # Create new
                    new_opp = Opportunity(**mapped_data)
                    new_opp.last_synced_at = datetime.utcnow()
                    # Set default workflow status if new
                    new_opp.workflow_status = "NEW" 
                    db.add(new_opp)
                    metrics["created"] += 1
                
                # Spontaneous Save: Commit after every item (or small batch)
                # This ensures that even if the process crashes later, this record is saved.
                db.commit() 
                
            except Exception as e:
                db.rollback() # Rollback only this transaction
                logger.error(f"Error syncing item {item.get('OptyId')}: {e}")
                metrics["errors"] += 1
                continue
        
        logger.info(f"Sync complete. Metrics: {metrics}")
        return {"status": "success", "metrics": metrics}

    except Exception as e:
        logger.error(f"Critical Sync Error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if should_close:
            db.close()


