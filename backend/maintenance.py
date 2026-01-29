
import os
import sys
import logging
from sqlalchemy import create_engine, text

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))

from backend.app.core.database import init_db, DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_and_migrate():
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    with engine.connect() as conn:
        logger.info("--- 1. Inspecting Tables ---")
        
        # Check row counts
        try:
            res_plural = conn.execute(text("SELECT count(*) FROM opportunities")).scalar()
            logger.info(f"Existing 'opportunities' count: {res_plural}")
        except:
            res_plural = -1 # Doesn't exist
            logger.info("'opportunities' table does not exist.")

        try:
            res_singular = conn.execute(text("SELECT count(*) FROM opportunity")).scalar()
            logger.info(f"Existing 'opportunity' count: {res_singular}")
        except:
            res_singular = -1
            logger.info("'opportunity' table does not exist.")

        # --- 2. Data Preservation / Migration ---
        if res_plural > 0:
            if res_singular <= 0:
                logger.info("Migrating data: Renaming 'opportunities' -> 'opportunity'...")
                try:
                    conn.execute(text("ALTER TABLE opportunities RENAME TO opportunity"))
                    logger.info("✅ Renamed successfully.")
                except Exception as e:
                    logger.error(f"Rename failed: {e}")
            else:
                logger.warning("Both tables exist and have data (or target exists). Manual merge might be needed, but proceeding to keep 'opportunity'.")
        
        # --- 3. Drop Auxiliary Tables ---
        logger.info("--- 3. Dropping Auxiliary Tables ---")
        tables_to_drop = [
            "opp_score_section_values", # New name
            "opp_score_section_value", # Old name
            "opp_score_version",       # Child of opportunity, user
            "opportunity_assignment",  # Child of opportunity, user
            "user_role",               # Child of user, role
            "app_user",                # Referenced by others
            "role",
            "sync_run",
            "opp_score_section"
        ]
        
        for t in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
                logger.info(f"Dropped {t}")
            except Exception as e:
                logger.warning(f"Could not drop {t}: {e}")

        # --- 4. Re-Initialize ---
        logger.info("--- 4. Re-Initializing Schema & Seeding ---")
    
    # Dispose engine to release locks before init_db
    engine.dispose()
    
    # Run standard init
    init_db()
    logger.info("--- 5. Final Metadata Sync ---")
    Base.metadata.create_all(bind=create_engine(DATABASE_URL))
    
    logger.info("✅ Maintenance Complete. Database is ready.")

if __name__ == "__main__":
    reset_and_migrate()
