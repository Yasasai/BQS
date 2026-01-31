import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

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
    workflow_status = Column(String, nullable=True) # NEW, ASSIGNED_TO_SA, UNDER_ASSESSMENT, APPROVED, REJECTED, etc.
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
    attachment_name = Column(String, nullable=True) # Added for evidence upload

    opportunity = relationship("Opportunity", back_populates="score_versions")
    section_values = relationship("OppScoreSectionValue", back_populates="score_version")

class OppScoreSection(Base):
    __tablename__ = "opp_score_section"
    section_code = Column(String, primary_key=True) 
    section_name = Column(String)
    display_order = Column(Integer)
    weight = Column(Float, default=1.0)

class OppScoreSectionValue(Base):
    __tablename__ = "opp_score_values"
    score_value_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    score_version_id = Column(String, ForeignKey("opp_score_version.score_version_id"), nullable=False)
    section_code = Column(String, ForeignKey("opp_score_section.section_code"), nullable=False)
    
    score = Column(Float, nullable=False) 
    notes = Column(Text, nullable=True)
    selected_reasons = Column(JSON, nullable=True) 

    score_version = relationship("OppScoreVersion", back_populates="section_values")
    section = relationship("OppScoreSection")
