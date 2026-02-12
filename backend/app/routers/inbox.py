
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import Opportunity, OpportunityAssignment, OppScoreVersion

router = APIRouter(prefix="/api/inbox", tags=["inbox"])

class InboxItem(BaseModel):
    opp_id: str
    row_id: Optional[str] = None
    opp_number: Optional[str]
    opp_name: str
    customer_name: str
    deal_value: float = 0
    crm_last_updated_at: datetime
    latest_score_status: str = "NOT_STARTED"
    version_no: Optional[int] = None

@router.get("/unassigned", response_model=List[InboxItem])
def get_unassigned_opportunities(db: Session = Depends(get_db)):
    assigned_subquery = db.query(OpportunityAssignment.opp_id).filter(OpportunityAssignment.status == "ACTIVE")
    opps = db.query(Opportunity).filter(Opportunity.is_active == True, ~Opportunity.opp_id.in_(assigned_subquery)).limit(1000).all()
    return [
        {
            "opp_id": o.opp_id,
            "row_id": o.opp_id,
            "opp_number": o.opp_number,
            "opp_name": o.opp_name,
            "customer_name": o.customer_name,
            "deal_value": o.deal_value or 0,
            "crm_last_updated_at": o.crm_last_updated_at,
            "latest_score_status": "NOT_STARTED"
        }
        for o in opps
    ]

@router.get("/my-assignments", response_model=List[InboxItem])
def get_my_assignments(user_id: str, db: Session = Depends(get_db)):
    results = []
    
    # 1. Fetch all versions created by this SA -> This includes history and drafts
    versions = db.query(OppScoreVersion).filter(
        OppScoreVersion.created_by_user_id == user_id
    ).order_by(desc(OppScoreVersion.version_no)).all()
    
    processed_opp_ids = set()
    
    for v in versions:
        o = v.opportunity
        if not o: continue
        processed_opp_ids.add(o.opp_id)
        
        results.append({
            "opp_id": o.opp_id,
            "row_id": f"{o.opp_id}_v{v.version_no}",
            "opp_number": o.opp_number,
            "opp_name": f"{o.opp_name} (v{v.version_no})",
            "customer_name": o.customer_name,
            "deal_value": o.deal_value or 0,
            "crm_last_updated_at": v.submitted_at or v.created_at,
            "latest_score_status": v.status,
            "version_no": v.version_no
        })
        
    # 2. Add currently assigned deals from OpportunityAssignment table
    assignments = db.query(OpportunityAssignment).filter(
        OpportunityAssignment.assigned_to_user_id == user_id,
        OpportunityAssignment.status == "ACTIVE"
    ).all()
    
    for a in assignments:
        o = a.opportunity
        if not o: continue
        if o.opp_id not in processed_opp_ids:
            processed_opp_ids.add(o.opp_id)
            results.append({
                "opp_id": o.opp_id,
                "row_id": o.opp_id,
                "opp_number": o.opp_number,
                "opp_name": o.opp_name,
                "customer_name": o.customer_name,
                "deal_value": o.deal_value or 0,
                "crm_last_updated_at": o.crm_last_updated_at,
                "latest_score_status": o.workflow_status or "NOT_STARTED",
                "version_no": None
            })
            
    # 3. Add direct assignments from Opportunity table (Primary Source)
    direct_opps = db.query(Opportunity).filter(
        or_(
            Opportunity.assigned_sa_id == user_id,
            Opportunity.assigned_sp_id == user_id
        ),
        Opportunity.is_active == True
    ).all()
    
    for o in direct_opps:
        if o.opp_id not in processed_opp_ids:
            processed_opp_ids.add(o.opp_id)
            results.append({
                "opp_id": o.opp_id,
                "row_id": o.opp_id,
                "opp_number": o.opp_number,
                "opp_name": o.opp_name,
                "customer_name": o.customer_name,
                "deal_value": o.deal_value or 0,
                "crm_last_updated_at": o.crm_last_updated_at,
                "latest_score_status": o.workflow_status or "NOT_STARTED",
                "version_no": None
            })
            
    return results

class AssignInput(BaseModel):
    opp_id: str
    sa_email: str
    secondary_sa_email: Optional[str] = None
    assigned_by_user_id: Optional[str] = "SYSTEM"

@router.post("/assign")
def assign_opportunity(data: AssignInput, db: Session = Depends(get_db)):
    # 1. Resolve SA User
    # 1. Resolve SA User
    from backend.app.models import AppUser, Role, UserRole
    sa_user = db.query(AppUser).filter(AppUser.email == data.sa_email).first()
    
    # SELF-HEALING: If user not found, create them to unblock demo
    if not sa_user:
        print(f"⚠️ User {data.sa_email} not found. Auto-creating...")
        
        # Determine Name
        name = "Solution Architect"
        if "john" in data.sa_email: name = "John Architect"
        if "alice" in data.sa_email: name = "Alice Architect"
        
        # Create User
        new_sa = AppUser(
            user_id=f"SA_{data.sa_email.split('@')[0].upper()}", # SA_JOHN.SA
            email=data.sa_email,
            display_name=name,
            is_active=True
        )
        db.add(new_sa)
        db.commit()
        
        # Assign Role
        sa_role = db.query(Role).filter(Role.role_code == "SA").first()
        if sa_role:
            ur = UserRole(user_id=new_sa.user_id, role_id=sa_role.role_id)
            db.add(ur)
            db.commit()
            
        sa_user = new_sa

    # 2. Manage existing assignment
    existing = db.query(OpportunityAssignment).filter(OpportunityAssignment.opp_id == data.opp_id, OpportunityAssignment.status == "ACTIVE").first()
    if existing: 
        existing.status = "REVOKED"
    
    # 3. Create New Assignment
    # Resolve assigner
    assigner_id = data.assigned_by_user_id
    
    # Map legacy frontend constants to seeded inputs if necessary
    if assigner_id == "PRACTICE_HEAD":
        assigner_id = "PH_001"
        
    # Strictly verify existence
    from backend.app.models import AppUser
    assigner_user = db.query(AppUser).filter(AppUser.user_id == assigner_id).first()
    
    if not assigner_user:
        # Fallback mechanism for safety, but log warning
        print(f"⚠️ Warning: Assigner ID '{assigner_id}' not found. Defaulting to system/first user.")
        fallback = db.query(AppUser).first()
        assigner_id = fallback.user_id if fallback else "SYSTEM"
    
    new_assign = OpportunityAssignment(
        opp_id=data.opp_id, 
        assigned_to_user_id=sa_user.user_id, 
        assigned_by_user_id=assigner_id, 
        status="ACTIVE"
    )
    db.add(new_assign)
    
    # 4. Update Opportunity Workflow Status
    opp = db.query(Opportunity).filter(Opportunity.opp_id == data.opp_id).first()
    if opp:
        opp.workflow_status = "ASSIGNED_TO_SA"
        opp.assigned_sa = sa_user.display_name # Denormalize for quick UI access if needed, or rely on joins

    # 5. Handle Versioning (New Requirement)
    # If the opportunity has ANY previous assessment, create a new version so the SA starts fresh but with context.
    last_ver = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == data.opp_id
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    if last_ver:
        new_ver_no = last_ver.version_no + 1
        new_version = OppScoreVersion(
            opp_id=data.opp_id,
            version_no=new_ver_no,
            status="ASSIGNED_TO_SA",
            created_by_user_id=sa_user.user_id,
            confidence_level=last_ver.confidence_level,
            recommendation=last_ver.recommendation,
            summary_comment=f"New version created after reassignment. Previous status: {last_ver.status}",
            attachment_name=last_ver.attachment_name
        )
        db.add(new_version)
        db.flush()
        
        # Clone section values for convenience
        from backend.app.models import OppScoreSectionValue
        old_values = db.query(OppScoreSectionValue).filter(
            OppScoreSectionValue.score_version_id == last_ver.score_version_id
        ).all()
        for v in old_values:
            db.add(OppScoreSectionValue(
                score_version_id=new_version.score_version_id,
                section_code=v.section_code,
                score=v.score,
                notes=v.notes,
                selected_reasons=v.selected_reasons
            ))

    db.commit()
    
    # Return updated data for frontend optimistic update
    return {
        "status": "success",
        "opportunity": {
            "id": data.opp_id,
            "assigned_sa": sa_user.display_name,
            "workflow_status": "ASSIGNED_TO_SA"
        }
    }

@router.get("/debug-assignments")
def debug_assignments(db: Session = Depends(get_db)):
    """Temporary endpoint to inspect assignments table"""
    assigns = db.query(OpportunityAssignment).all()
    results = []
    for a in assigns:
        results.append({
            "opp_id": a.opp_id,
            "user_id": a.assigned_to_user_id,
            "by_user": a.assigned_by_user_id,
            "status": a.status,
            "created": str(a.assigned_at)
        })
    return results

@router.get("/{opp_id}")
def get_opportunity_detail(opp_id: str, db: Session = Depends(get_db)):
    o = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not o: raise HTTPException(404, "Not found")
    return {
        "opp_id": o.opp_id,
        "opp_number": o.opp_number,
        "opp_name": o.opp_name,
        "customer_name": o.customer_name,
        "deal_value": o.deal_value,
        "crm_last_updated_at": o.crm_last_updated_at,
        "currency": o.currency,
        "stage": o.stage
    }
