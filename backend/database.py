
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import os
import uuid

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment")

Base = declarative_base()

# --- 1. REFERENCE / SECURITY ---

class AppUser(Base):
    __tablename__ = "app_user"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="user")

class Role(Base):
    __tablename__ = "role"
    role_id = Column(Integer, primary_key=True) # 1=Admin, 2=SA, etc
    role_code = Column(String, unique=True)     # SA, SALES_LEAD
    role_name = Column(String)

class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(String, ForeignKey("app_user.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.role_id"), primary_key=True)
    
    user = relationship("AppUser", back_populates="user_roles")
    role = relationship("Role")

# --- 2. CRM SYNCED CORE ---

class Practice(Base):
    __tablename__ = "practice"
    practice_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    practice_code = Column(String, unique=True) 
    practice_name = Column(String, nullable=False)

class Opportunity(Base):
    __tablename__ = "opportunity"
    
    opp_id = Column(String, primary_key=True) # The Oracle OptyId
    opp_number = Column(String) 
    
    opp_name = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    geo = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    deal_value = Column(Float, nullable=True)
    stage = Column(String, nullable=True)
    close_date = Column(DateTime, nullable=True)
    
    sales_owner_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    primary_practice_id = Column(String, ForeignKey("practice.practice_id"), nullable=True)
    
    crm_last_updated_at = Column(DateTime, nullable=False)
    local_last_synced_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    assignments = relationship("OpportunityAssignment", back_populates="opportunity")
    score_versions = relationship("OppScoreVersion", back_populates="opportunity")

class SyncRun(Base):
    __tablename__ = "sync_run"
    sync_run_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String) 
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    rows_upserted = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

# --- 3. ASSIGNMENT ---

class OpportunityAssignment(Base):
    __tablename__ = "opportunity_assignment"
    assignment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opp_id = Column(String, ForeignKey("opportunity.opp_id"), nullable=False)
    assigned_to_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=False)
    assigned_by_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ACTIVE") # ACTIVE, REVOKED

    opportunity = relationship("Opportunity", back_populates="assignments")

# --- 4. SCORING ---

class OppScoreVersion(Base):
    __tablename__ = "opp_score_version"
    score_version_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opp_id = Column(String, ForeignKey("opportunity.opp_id"), nullable=False)
    version_no = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # DRAFT, SUBMITTED
    
    overall_score = Column(Integer, nullable=True)
    confidence_level = Column(String, nullable=True) 
    recommendation = Column(String, nullable=True)   
    summary_comment = Column(Text, nullable=True)
    
    created_by_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    opportunity = relationship("Opportunity", back_populates="score_versions")
    section_values = relationship("OppScoreSectionValue", back_populates="score_version")

class OppScoreSection(Base):
    __tablename__ = "opp_score_section"
    section_code = Column(String, primary_key=True) 
    section_name = Column(String)
    display_order = Column(Integer)
    weight = Column(Float, default=1.0)

class OppScoreSectionValue(Base):
    __tablename__ = "opp_score_section_value"
    score_value_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    score_version_id = Column(String, ForeignKey("opp_score_version.score_version_id"), nullable=False)
    section_code = Column(String, ForeignKey("opp_score_section.section_code"), nullable=False)
    
    score = Column(Integer, nullable=False) # 1..5
    notes = Column(Text, nullable=True)

    score_version = relationship("OppScoreVersion", back_populates="section_values")

# --- 6. SETUP & SEEDING ---

def init_db():
    try:
        db_user = os.getenv("POSTGRES_USER", "postgres")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        conn = psycopg2.connect(dbname='postgres', user=db_user, host=db_host, password=db_password, port=db_port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE bqs")
                print("✅ Database 'bqs' created.")
        conn.close()
    except Exception as e:
        print(f"Startup DB Check: {e}")

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    
    # Seed Data
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Roles - Read from INITIAL_ROLES env var
        if not db.query(Role).first():
            roles_env = os.getenv("INITIAL_ROLES", "1:SALES_LEAD:Sales Lead,2:SA:Solution Architect")
            roles_to_add = []
            for item in roles_env.split(","):
                try:
                    rid, rcode, rname = item.split(":")
                    roles_to_add.append(Role(role_id=int(rid), role_code=rcode, role_name=rname))
                except ValueError:
                    pass
            if roles_to_add:
                db.add_all(roles_to_add)
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
