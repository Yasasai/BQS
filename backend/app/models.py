import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

# --- 1. REFERENCE / SECURITY ---

class AppUser(Base):
    __tablename__ = "app_user"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    manager_email = Column(String, nullable=True)
    corporate_title = Column(String, nullable=True)
    geo_region = Column(String, nullable=True)
    practice_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
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
    opp_number = Column(String, index=True) 
    
    opp_name = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    geo = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    deal_value = Column(Float, nullable=False)
    stage = Column(String, nullable=False)
    close_date = Column(DateTime, nullable=True)
    
    sales_owner_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    primary_practice_id = Column(String, ForeignKey("practice.practice_id"), nullable=True)
    
    crm_last_updated_at = Column(DateTime, nullable=False)
    local_last_synced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    workflow_status = Column(String, nullable=False, index=True) # NEW, ASSIGNED_TO_SA, UNDER_ASSESSMENT, APPROVED, REJECTED, etc.
    is_active = Column(Boolean, default=True)

    # --- New MVP Fields ---
    margin_percentage = Column(Float, nullable=True)
    pat_margin = Column(Float, nullable=True)

    # --- Workflow Assignment Columns ---
    assigned_practice_head_ids = Column(JSON, nullable=True) # List of user_ids
    assigned_sales_head_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    assigned_sa_ids = Column(JSON, nullable=True) # List of user_ids
    assigned_sp_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    assigned_finance_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    assigned_legal_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    bid_manager_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)

    # --- Approval Status Columns ---
    gh_approval_status = Column(String, default='PENDING', nullable=True) # PENDING, APPROVED, REJECTED
    ph_approval_status = Column(String, default='PENDING', nullable=True)
    sh_approval_status = Column(String, default='PENDING', nullable=True)
    finance_approval_status = Column(String, default='PENDING')
    legal_approval_status = Column(String, default='PENDING')
    
    combined_submission_ready = Column(Boolean, default=False)

    # --- Locking Columns ---
    locked_by = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    locked_at = Column(DateTime, nullable=True)

    # --- Lifecycle Closure Columns ---
    close_reason = Column(String, nullable=True)      # WON or LOST
    closed_by = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    reopened_by = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    reopened_at = Column(DateTime, nullable=True)

    # Relationships
    user_locked = relationship("AppUser", foreign_keys=[locked_by])
    assignments = relationship("OpportunityAssignment", back_populates="opportunity")
    score_versions = relationship("OppScoreVersion", back_populates="opportunity")

class SyncRun(Base):
    __tablename__ = "sync_run"
    sync_run_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String) 
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    rows_upserted = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

class DocumentCategory(Base):
    __tablename__ = "document_category"
    category_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label_name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

# --- 3. ASSIGNMENT ---

class OpportunityAssignment(Base):
    __tablename__ = "opportunity_assignment"
    assignment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opp_id = Column(String, ForeignKey("opportunity.opp_id"), nullable=False, index=True)
    assigned_to_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=False, index=True)
    assigned_by_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="ACTIVE") # ACTIVE, REVOKED

    opportunity = relationship("Opportunity", back_populates="assignments")

# --- 4. SCORING ---

class OppScoreVersion(Base):
    __tablename__ = "opp_score_version"
    __table_args__ = (
        UniqueConstraint('opp_id', 'version_no', name='unique_opp_version'),
    )
    score_version_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opp_id = Column(String, ForeignKey("opportunity.opp_id"), nullable=False)
    version_no = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # DRAFT, SUBMITTED
    
    overall_score = Column(Integer, nullable=True)
    confidence_level = Column(String, nullable=True) 
    recommendation = Column(String, nullable=True)   
    summary_comment = Column(Text, nullable=True)
    
    created_by_user_id = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    sa_submitted = Column(Boolean, default=False)
    sp_submitted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
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
    reasons = Column(JSON, nullable=True) # Added for Task 2/3 Single Source of Truth

class OppScoreSectionValue(Base):
    __tablename__ = "opp_score_values"
    __table_args__ = (
        CheckConstraint('score >= 0.0 AND score <= 5.0', name='check_score_range'),
    )
    score_value_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    score_version_id = Column(String, ForeignKey("opp_score_version.score_version_id"), nullable=False, index=True)
    section_code = Column(String, ForeignKey("opp_score_section.section_code"), nullable=False, index=True)
    
    score = Column(Float, nullable=False) 
    notes = Column(Text, nullable=True)
    selected_reasons = Column(JSON, nullable=True) 

    score_version = relationship("OppScoreVersion", back_populates="section_values")
    section = relationship("OppScoreSection")

# --- 5. SYSTEM META ---

class SyncMeta(Base):
    __tablename__ = "sync_meta"
    meta_key = Column(String, primary_key=True) # e.g. 'oracle_opportunities'
    last_sync_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sync_status = Column(String, nullable=True) # SUCCESS, FAILED
    records_processed = Column(Integer, default=0)
    extra_info = Column(JSON, nullable=True)

# --- 6. CONNECTIVITY VERIFICATION ---

class OracleOpportunity(Base):
    """
    Staging table for Oracle CRM opportunities.
    """
    __tablename__ = "oracle_opportunities"
    
    opty_id = Column(String, primary_key=True)
    opty_number = Column(String, nullable=True)
    name = Column(String, nullable=True)
    target_party_name = Column(String, nullable=True)
    revenue = Column(Float, nullable=True)
    currency_code = Column(String, nullable=True)
    sales_stage = Column(String, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    last_update_date = Column(DateTime, nullable=True)
    opty_last_update_date = Column(DateTime, nullable=True)
    practice_c = Column(String, nullable=True)
    geo_c = Column(String, nullable=True)
    crm_link = Column(String, nullable=True)
    raw_json = Column(JSON, nullable=True)
    synced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# --- 7. CRM BATCH SYNC MODELS ---

class CRMSyncRun(Base):
    __tablename__ = "crm_sync_run"
    sync_run_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime, nullable=True)
    status = Column(String, nullable=False) # RUNNING / SUCCESS / FAILED
    total_records_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

class CRMSyncWatermark(Base):
    __tablename__ = "crm_sync_watermark"
    object_name = Column(String, primary_key=True) # e.g. 'opportunities'
    last_offset = Column(Integer, default=0)
    last_successful_sync_time = Column(DateTime, nullable=True)

class CRMSyncError(Base):
    __tablename__ = "crm_sync_error"
    error_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("crm_sync_run.sync_run_id"), nullable=False)
    api_endpoint = Column(String, nullable=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CRMOpportunity(Base):
    __tablename__ = "crm_opportunity"
    opty_id = Column(String, primary_key=True) # Primary Key
    opty_number = Column(String, unique=True, index=True)
    opportunity_name = Column(String, nullable=False)
    account_name = Column(String, nullable=True)
    revenue = Column(Float, nullable=True)
    currency_code = Column(String, nullable=True)
    sales_stage = Column(String, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    last_update_date = Column(DateTime, nullable=True)
    opty_last_update_date = Column(DateTime, nullable=True)
    practice = Column(String, nullable=True)
    geo = Column(String, nullable=True)
    crm_link = Column(String, nullable=True)
    
    # Audit fields (optional but good for tracking)
    last_seen_ts = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_synced_run_id = Column(String, ForeignKey("crm_sync_run.sync_run_id"), nullable=True)

class CRMOpportunityResource(Base):
    __tablename__ = "crm_opportunity_resource"
    resource_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opty_id = Column(String, ForeignKey("crm_opportunity.opty_id"), nullable=False, index=True)
    resource_name = Column(String, nullable=True)
    salesrep_number = Column(String, nullable=True)
    role_code = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    last_seen_ts = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_synced_run_id = Column(String, ForeignKey("crm_sync_run.sync_run_id"), nullable=True)

class CRMSalesRep(Base):
    __tablename__ = "crm_sales_rep"
    salesrep_number = Column(String, primary_key=True)
    party_name = Column(String, nullable=True)
    email_address = Column(String, nullable=True)
    last_seen_ts = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_synced_run_id = Column(String, ForeignKey("crm_sync_run.sync_run_id"), nullable=True)

# --- 8. SYSTEM CONFIGURATION ---

class SystemConfig(Base):
    """
    Key-value store for system-wide configuration values.
    Used for GO/NO-GO threshold and other admin-configurable parameters.
    """
    __tablename__ = "system_config"
    config_key = Column(String, primary_key=True)  # e.g. 'go_no_go_threshold_percent'
    config_value = Column(JSON, nullable=False)      # stored as JSON for flexibility
    updated_by = Column(String, ForeignKey("app_user.user_id"), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
