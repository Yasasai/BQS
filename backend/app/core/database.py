
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, Role, AppUser, UserRole, OppScoreSection, OppScoreVersion, OppScoreSectionValue, Opportunity, OpportunityAssignment, Practice, SyncRun, SyncMeta, OracleOpportunity

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def init_db():
    """Checks if DB exists, creates it if not, and seeds initial data."""
    try:
        # Connect to default 'postgres' db to check if 'bqs' exists
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', password='Abcd1234', port=5432)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE bqs")
                print("Database 'bqs' created.")
        conn.close()
    except Exception as e:
        print(f"Startup DB Check: {e}")

    # Now connect to the actual DB
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    echo=True
    Base.metadata.create_all(bind=engine)
    
    # NEW: Run self-healing to ensure justifications/reasons columns exist
    from backend.app.core.self_healing import heal_database
    heal_database(engine)
    
    # Seed Data
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Roles
        if not db.query(Role).first():
            db.add_all([
                Role(role_id=1, role_code="GH", role_name="Global Head"),
                Role(role_id=2, role_code="PH", role_name="Practice Head"),
                Role(role_id=3, role_code="SH", role_name="Sales Head"),
                Role(role_id=4, role_code="SA", role_name="Solution Architect"),
                Role(role_id=5, role_code="SP", role_name="Sales Person")
            ])
            db.flush()

        # Sections - Synchronized with Frontend ScoreOpportunity.tsx
        required_sections = [
            ("STRAT", "Strategic Fit", 1, 0.15),
            ("WIN", "Win Probability", 2, 0.15),
            ("FIN", "Financial Value", 3, 0.15),
            ("COMP", "Competitive Position", 4, 0.10),
            ("FEAS", "Delivery Feasibility", 5, 0.10),
            ("CUST", "Customer Relationship", 6, 0.10),
            ("RISK", "Risk Exposure", 7, 0.10),
            ("PROD", "Product / Service Compliance", 8, 0.05),
            ("LEGAL", "Legal & Commercial Readiness", 9, 0.10)
        ]
        
        for code, name, order, weight in required_sections:
            existing = db.query(OppScoreSection).filter_by(section_code=code).first()
            if not existing:
                db.add(OppScoreSection(section_code=code, section_name=name, display_order=order, weight=weight))
            else:
                existing.section_name = name
                existing.display_order = order
                existing.weight = weight
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seeding Error: {e}")
    finally:
        db.close()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
