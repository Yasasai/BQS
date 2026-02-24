
import os
import sys
from datetime import datetime
import logging

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import OracleOpportunity
from backend.app.services.oracle_service import get_all_opportunities

# Setup logging without emojis for Windows compatibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_connectivity():
    logger.info("Starting Backend Connectivity Check...")
    
    # 1. Initialize DB (Creates the oracle_opportunities table)
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    db = SessionLocal()
    total_saved = 0
    
    try:
        logger.info("Fetching ALL opportunities from Oracle CRM into isolated table...")
        
        # Loop through batches yielded by get_all_opportunities
        for batch in get_all_opportunities(batch_size=50):
            if not batch:
                continue

            logger.info(f"Received {len(batch)} records from Oracle. Saving to oracle_opportunities...")

            for item in batch:
                opty_id = str(item.get("OptyId"))
                
                # Simple parsing for dates
                last_update = None
                lu_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
                if lu_str:
                    try:
                        last_update = datetime.fromisoformat(lu_str.replace('Z', '+00:00'))
                    except: pass

                # Create verification record
                oracle_opp = OracleOpportunity(
                    opty_id=opty_id,
                    opty_number=str(item.get("OptyNumber")),
                    name=item.get("Name"),
                    account_name=item.get("TargetPartyName"),
                    revenue=float(item.get("Revenue") or 0),
                    currency=item.get("CurrencyCode"),
                    sales_stage=item.get("SalesStage"),
                    last_update_date=last_update,
                    raw_json=item
                )
                
                # Check for existence
                existing = db.query(OracleOpportunity).filter(OracleOpportunity.opty_id == opty_id).first()
                if existing:
                    for key in ["opty_number", "name", "account_name", "revenue", "currency", "sales_stage", "last_update_date", "raw_json"]:
                        setattr(existing, key, getattr(oracle_opp, key))
                else:
                    db.add(oracle_opp)
                
                total_saved += 1

            # Commit after each batch
            db.commit()
            logger.info(f"Progress: {total_saved} total records saved/updated.")

        logger.info("Verification Complete. Total records in isolated table: " + str(total_saved))
        logger.info(f"Successfully saved/updated {total_saved} records in 'oracle_opportunities'.")
        logger.info("Backend connectivity verification: COMPLETED.")

    except Exception as e:
        logger.error(f"Error during connectivity check: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_connectivity()
