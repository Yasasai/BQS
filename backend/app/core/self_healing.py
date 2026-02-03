
from sqlalchemy import create_engine, inspect, text
import logging

logger = logging.getLogger(__name__)

def heal_database(engine):
    """
    Vibrant self-healing routine for BQS database.
    Ensures that the schema matches expectations exactly, 
    adding missing columns for justifications (reasons) if they're gone.
    """
    logger.info("🛠️ Running Database Self-Healing...")
    insp = inspect(engine)
    
    # 1. Ensure Table naming alignment
    # If the old table exists and the new one doesn't, rename it.
    tables = insp.get_table_names()
    
    if "opp_score_section_values" in tables and "opp_score_values" not in tables:
        logger.warning("🔄 Found legacy table 'opp_score_section_values'. Renaming to 'opp_score_values'...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE opp_score_section_values RENAME TO opp_score_values;"))
            conn.commit()
            tables = inspect(engine).get_table_names() # Refresh

    # 2. Heal the primary results table: opp_score_values
    if "opp_score_values" in tables:
        cols = [c['name'] for c in insp.get_columns("opp_score_values")]
        
        # Ensure selected_reasons (justifications) exists
        if "selected_reasons" not in cols:
            logger.warning("🩹 Healing 'opp_score_values': Adding missing 'selected_reasons' column.")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE opp_score_values ADD COLUMN selected_reasons JSON;"))
                conn.commit()

        # Ensure notes exists
        if "notes" not in cols:
            logger.warning("🩹 Healing 'opp_score_values': Adding missing 'notes' column.")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE opp_score_values ADD COLUMN notes TEXT;"))
                conn.commit()

        # Ensure score is float for 0.5 steps
        for c in insp.get_columns("opp_score_values"):
            if c['name'] == 'score' and 'INT' in str(c['type']).upper():
                logger.warning("🩹 Healing 'opp_score_values': Migrating 'score' from Integer to Float.")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE opp_score_values ALTER COLUMN score TYPE FLOAT;"))
                    conn.commit()

    # 3. Heal the version table
    if "opp_score_version" in tables:
        cols = [c['name'] for c in insp.get_columns("opp_score_version")]
        if "attachment_name" not in cols:
            logger.warning("🩹 Healing 'opp_score_version': Adding missing 'attachment_name' column.")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE opp_score_version ADD COLUMN attachment_name VARCHAR;"))
                conn.commit()

    # 4. Heal the opportunity table
    if "opportunity" in tables:
        cols = [c['name'] for c in insp.get_columns("opportunity")]
        if "workflow_status" not in cols:
            logger.warning("🩹 Healing 'opportunity': Adding missing 'workflow_status' column.")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE opportunity ADD COLUMN workflow_status VARCHAR;"))
                conn.commit()
        
        # Sync workflow_status from latest assessment versions
        logger.info("🔄 Syncing workflow_status from assessment data...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE opportunity o
                SET workflow_status = CASE
                    WHEN v.status = 'SUBMITTED' THEN 'SUBMITTED_FOR_REVIEW'
                    WHEN v.status = 'DRAFT' THEN 'UNDER_ASSESSMENT'
                    WHEN v.status = 'APPROVED' THEN 'APPROVED'
                    WHEN v.status = 'REJECTED' THEN 'REJECTED'
                    WHEN v.status = 'ACCEPTED' THEN 'ACCEPTED'
                    ELSE v.status
                END
                FROM (
                    SELECT DISTINCT ON (opp_id) opp_id, status
                    FROM opp_score_version
                    ORDER BY opp_id, version_no DESC
                ) v
                WHERE o.opp_id = v.opp_id AND o.workflow_status IS NULL
            """))
            conn.commit()
            if result.rowcount > 0:
                logger.info(f"✅ Synced workflow_status for {result.rowcount} opportunities")

    logger.info("✨ Database Health Check: Passed.")
