
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

    logger.info("✨ Database Health Check: Passed.")
