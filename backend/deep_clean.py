
import os
import sys
import logging
import psycopg2
from sqlalchemy import create_engine, text

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(BASE_DIR))

from backend.app.core.database import init_db, DATABASE_URL
from backend.app.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deep_clean():
    logger.info("--- 1. DEEP CLEAN: Dropping all known score tables ---")
    
    # Use raw psycopg2 for forced cascade drop
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        with conn.cursor() as cur:
            tables = [
                "opp_score_values", "opp_score_section_values", "opp_score_section_value",
                "opp_score_version", "opp_score_section", "opportunity_assignment",
                "user_role", "app_user", "role", "sync_run"
            ]
            for t in tables:
                cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE;")
                logger.info(f"Dropped {t}")
        conn.close()
    except Exception as e:
        logger.error(f"Drop failed: {e}")

    logger.info("--- 2. RE-INITIALIZING ---")
    
    # This will recreate tables based on the updated models.py
    init_db()
    
    # Final metadata sync just in case
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Database deep clean and re-init complete.")

if __name__ == "__main__":
    deep_clean()
