
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, Role, AppUser, UserRole, OppScoreSection

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
                print("✅ Database 'bqs' created.")
        conn.close()
    except Exception as e:
        print(f"Startup DB Check: {e}")

    # Now connect to the actual DB
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    
    # Seed Data
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Roles
        if not db.query(Role).first():
            db.add_all([
                Role(role_id=1, role_code="SALES_LEAD", role_name="Sales Lead"),
                Role(role_id=2, role_code="SA", role_name="Solution Architect")
            ])
            db.flush()

        # Users
        if not db.query(AppUser).filter_by(email="kunal.lead@example.com").first():
            kunal = AppUser(email="kunal.lead@example.com", display_name="Kunal (Lead)")
            db.add(kunal)
            db.flush()
            db.add(UserRole(user_id=kunal.user_id, role_id=1))
            
        if not db.query(AppUser).filter_by(email="sa.demo@example.com").first():
            sa = AppUser(email="sa.demo@example.com", display_name="Demo SA")
            db.add(sa)
            db.flush()
            db.add(UserRole(user_id=sa.user_id, role_id=2))

        # Sections
        if not db.query(OppScoreSection).first():
            db.add_all([
                OppScoreSection(section_code="FIT", section_name="Fit & Strategic Alignment", display_order=1),
                OppScoreSection(section_code="DELIVERY", section_name="Delivery Readiness", display_order=2),
                OppScoreSection(section_code="COMMERCIAL", section_name="Commercial Attractiveness", display_order=3),
                OppScoreSection(section_code="RISK", section_name="Risk & Complexity", display_order=4)
            ])
            
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
