
import os
import sys
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("bqs_checker")

def check_legal_lead_connection():
    # 1. Resolve DB Connection
    backend_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(backend_path, ".env")
    
    database_url = None
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    database_url = line.split("=", 1)[1].strip().strip('"')
    
    if not database_url:
        logger.error("COULD NOT FIND DATABASE_URL in backend/.env")
        return

    # 2. Connect to Database
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info("Connected to database.")
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        return

    # 3. Check Opportunity Table Schema for Legal Lead columns
    logger.info("--- SCHEMA CHECK: Opportunity Table ---")
    try:
        # Check for columns
        cols_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'opportunity' 
            AND column_name IN ('assigned_legal_id', 'legal_approval_status');
        """)
        cols = session.execute(cols_query).fetchall()
        col_names = [c[0] for c in cols]
        
        expected = ['assigned_legal_id', 'legal_approval_status']
        for col in expected:
            if col in col_names:
                dtype = [c[1] for c in cols if c[0] == col][0]
                logger.info(f"✅ Column '{col}' exists (Type: {dtype})")
            else:
                logger.error(f"❌ Column '{col}' IS MISSING from 'opportunity' table!")
    except Exception as e:
        logger.error(f"Schema check failed: {e}")

    # 4. Check Roles for LEGAL
    logger.info("--- ROLE CHECK: LEGAL Role ---")
    try:
        role_query = text("SELECT role_id, role_code, role_name FROM role WHERE role_code = 'LEGAL';")
        role = session.execute(role_query).fetchone()
        if role:
            logger.info(f"✅ Role 'LEGAL' exists (ID: {role[0]}, Name: {role[2]})")
        else:
            logger.error("❌ Role 'LEGAL' IS MISSING from 'role' table!")
    except Exception as e:
        logger.error(f"Role check failed: {e}")

    # 5. Check Users for LEGAL role
    logger.info("--- USER CHECK: Users with LEGAL role ---")
    try:
        users_query = text("""
            SELECT u.user_id, u.display_name, u.email 
            FROM app_user u
            JOIN user_role ur ON u.user_id = ur.user_id
            JOIN role r ON ur.role_id = r.role_id
            WHERE r.role_code = 'LEGAL' AND u.is_active = true;
        """)
        users = session.execute(users_query).fetchall()
        if users:
            for u in users:
                logger.info(f"✅ Found legal user: {u[1]} ({u[2]}) [ID: {u[0]}]")
        else:
            logger.warning("⚠️ No active users found with 'LEGAL' role assigned.")
    except Exception as e:
        logger.error(f"User check failed: {e}")

    # 6. Check Current Assignments
    logger.info("--- DATA CHECK: Current Legal Lead Assignments ---")
    try:
        assign_query = text("""
            SELECT opp_id, opp_number, opp_name, assigned_legal_id 
            FROM opportunity 
            WHERE assigned_legal_id IS NOT NULL 
            LIMIT 5;
        """)
        assigns = session.execute(assign_query).fetchall()
        if assigns:
            for a in assigns:
                logger.info(f"✅ Opportunity {a[1]} ('{a[2]}') has Legal Lead assigned ID: {a[3]}")
        else:
            logger.warning("⚠️ No opportunities currently have a Legal Lead assigned in the backend.")
    except Exception as e:
        logger.error(f"Assignment check failed: {e}")

    # 7. Check Scoring Version Table
    logger.info("--- SCHEMA CHECK: OppScoreVersion Table ---")
    try:
        # Some versions of this app might track legal lead per version too
        score_cols_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'opp_score_version' 
            AND column_name IN ('assigned_legal_id');
        """)
        score_cols = session.execute(score_cols_query).fetchall()
        if score_cols:
             logger.info("ℹ️ OppScoreVersion table has 'assigned_legal_id' column (Good for versioning history)")
        else:
             logger.info("ℹ️ OppScoreVersion table does NOT track legal lead per version (Optional based on design)")
    except Exception as e:
        logger.debug(f"OppScoreVersion check skipped: {e}")

    session.close()
    logger.info("--- CHECK COMPLETE ---")

if __name__ == "__main__":
    check_legal_lead_connection()
