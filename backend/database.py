import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def init_db():
    """Consolidated logic to ensure DB exists and tables are ready."""
    try:
        # Connect to default postgres to check for 'bqs'
        # Note: Using hardcoded credentials for local dev as requested. 
        # In production this should be more dynamic.
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', password='Abcd1234', port=5432)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE bqs")
        conn.close()
    except Exception as e:
        print(f"Startup DB Check: {e}")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Models ---

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    remote_id = Column(String, unique=True, index=True) # Oracle Opportunity Number
    name = Column(String)                               # Oracle Name
    customer = Column(String)                           # Oracle Account
    practice = Column(String)                           # Oracle Practice
    geo = Column(String)                                # GEO
    region = Column(String)                             # Region
    sector = Column(String)                             # Sector
    deal_value = Column(Float)
    currency = Column(String, default="USD")
    win_probability = Column(Float)                     # Oracle Win (%)
    sales_owner = Column(String)                        # Oracle Owner
    stage = Column(String)                               # Oracle Sales Stage (e.g., Bid Preparation)
    
    # Dates
    expected_po_date = Column(String)                   # Expected PO Date
    estimated_billing_date = Column(String)             # Oracle Estimated Billing Date
    close_date = Column(String)
    
    # --- STRICT STATE MACHINE ---
    # NEW | ASSIGNED_TO_PRACTICE | PENDING_ASSESSMENT | ...
    # mapped to user-friendly labels: New from CRM, Scoring Pending, etc.
    workflow_status = Column(String, default="New from CRM")
    status = Column(String, default="New from CRM") # Redundant but safe for frontend
    
    # Ownership
    assigned_sa = Column(String) # Solution Architect
    sa_owner = Column(String)    # redundant but used in some endpoints
    
    # Metadata for Governance
    sa_notes = Column(Text)
    practice_head_recommendation = Column(String) # APPROVE | REJECT
    practice_head_notes = Column(Text) # PH comments/rejection reasons
    assigned_practice = Column(String) # Practice assigned by management
    management_decision = Column(String) # BID | NO_BID
    close_reason = Column(Text)
    
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    assessments = relationship("Assessment", back_populates="opportunity")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    opp_id = Column(Integer, ForeignKey("opportunities.id"))
    version = Column(String)
    
    scores = Column(JSON)
    comments = Column(Text)
    risks = Column(JSON)
    
    is_submitted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)

    opportunity = relationship("Opportunity", back_populates="assessments")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String)

def get_db():
    """Dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
