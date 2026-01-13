import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs")

def init_db():
    """Consolidated logic to ensure DB exists, tables are created, and columns are synchronized."""
    from sqlalchemy import inspect, text
    
    try:
        # 1. Ensure the PostgreSQL database 'bqs' exists
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', password='Abcd1234', port=5432)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE bqs")
        conn.close()
    except Exception as e:
        print(f"Startup DB Check: {e}")

    # Create engine with robust connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # Check if connection is alive before using
        pool_recycle=1800     # Recycle connections every 30 minutes
    )
    
    # 2. Create Base tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # 3. SELF-HEALING: Check for missing columns in existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                # Compare model columns vs DB columns
                db_columns = {col['name'] for col in inspector.get_columns(table_name)}
                model_columns = {col.name for col in table.columns}
                missing = model_columns - db_columns
                
                if missing:
                    print(f"🔧 Healing table '{table_name}' (missing: {missing})")
                    for col_name in missing:
                        col = table.columns[col_name]
                        col_type = col.type.compile(dialect=engine.dialect)
                        nullable = "NULL" if col.nullable else "NOT NULL"
                        # Standard SQL to add column if not exists
                        sql = f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}'
                        db.execute(text(sql))
                    db.commit()
    except Exception as e:
        db.rollback()
        print(f"⚠️  Self-healing Warning: {e}")
    finally:
        db.close()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
)
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
    description = Column(Text)  # Added to primary model for easy UI access
    remote_url = Column(String) # Link back to Oracle CRM
    
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

class SyncLog(Base):
    """Track Oracle CRM sync operations"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String)  # FULL or INCREMENTAL
    status = Column(String)  # RUNNING, SUCCESS, FAILED
    
    total_fetched = Column(Integer, default=0)
    new_records = Column(Integer, default=0)
    updated_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    error_message = Column(String, nullable=True)
    sync_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved word)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

class OpportunityIDLog(Base):
    """Track historical changes for specific opportunities"""
    __tablename__ = "opportunity_id_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    opp_id = Column(String, index=True) # remote_id
    field_name = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)
    sync_id = Column(Integer, ForeignKey("sync_logs.id"))

class OpportunityDetails(Base):
    """Extended details captured from Oracle CRM UI fields"""
    __tablename__ = "opportunity_details"

    id = Column(Integer, primary_key=True, index=True)
    opty_number = Column(String, unique=True, index=True) # Master reference
    opty_id = Column(String)                             # Technical ID
    name = Column(String)
    account_name = Column(String)
    
    # Financials
    revenue = Column(Float, default=0.0)
    currency_code = Column(String, default="USD")
    win_probability = Column(Float, default=0.0)
    
    # Taxonomy
    practice = Column(String)
    geo = Column(String)
    region = Column(String)
    business_unit = Column(String)
    customer_sponsor = Column(String)
    primary_partner = Column(String)
    
    # Ownership & People
    owner_name = Column(String)
    primary_contact = Column(String)
    
    # Status & Dates
    sales_stage = Column(String)
    sales_method = Column(String)
    status_code = Column(String)
    status_label = Column(String)
    
    close_date = Column(String)
    effective_date = Column(String)
    last_update_date = Column(DateTime)
    creation_date = Column(DateTime)
    
    # Metadata
    description = Column(Text)
    raw_json = Column(JSON) # Store full Oracle JSON for auditing
    remote_url = Column(String) # Link back to Oracle CRM
    last_synced_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
