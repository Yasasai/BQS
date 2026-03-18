from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func, cast, String
from typing import List, Optional, Any
from datetime import datetime, date
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import Opportunity, OpportunityAssignment, OppScoreVersion, Practice, AppUser, OppScoreSectionValue, DocumentCategory
from backend.app.core.logging_config import get_logger
from backend.app.core.auth import get_current_user, require_role
from backend.app.services.workflow_service import handle_approval_action
from backend.app.services import opportunity_service

logger = get_logger("opportunities_router")


router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

@router.get("/metadata/{type}")
def get_opportunity_metadata(type: str, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    """
    Consolidated metadata endpoint for regions, practices, stages, etc.
    Safely returns default values if the database is empty.
    """
    try:
        if type == "regions":
            regions = db.query(Opportunity.geo).filter(Opportunity.geo.isnot(None), Opportunity.is_active == True).distinct().all()
            result = [r[0] for r in regions if r[0]]
            return result if result else ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East", "Africa"]
        
        elif type == "practices":
            # Pull from the Practice table primarily
            practices = db.query(Practice.practice_name).filter(Practice.is_active == True).all()
            result = [p[0] for p in practices if p[0]]
            if not result:
                # Fallback to distinct practices in Opportunity table if meta table is empty
                opp_practices = db.query(Opportunity.practice).filter(Opportunity.practice.isnot(None)).distinct().all()
                result = [p[0] for p in opp_practices if p[0]]
            return result if result else ["Digital Transformation", "Cloud Infrastructure", "Cybersecurity", "Data Analytics"]
            
        elif type == "stages":
            stages = db.query(Opportunity.stage).filter(Opportunity.stage.isnot(None), Opportunity.is_active == True).distinct().all()
            result = [s[0] for s in stages if s[0]]
            return result if result else ["Discovery", "Qualifying", "Solutioning", "Proposal", "Negotiation", "Closing"]
            
        elif type == "statuses":
            statuses = db.query(Opportunity.workflow_status).filter(Opportunity.workflow_status.isnot(None), Opportunity.is_active == True).distinct().all()
            result = [s[0] for s in statuses if s[0]]
            return result if result else ["NEW", "UNDER_ASSESSMENT", "READY_FOR_REVIEW", "APPROVED", "REJECTED"]
            
        return []
    except Exception as e:
        logger.error(f"Error fetching metadata for {type}: {e}")
        return []

# Legacy specific routes for backward compatibility
@router.get("/metadata/regions")
def get_unique_regions(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    return get_opportunity_metadata("regions", db, current_user)

@router.get("/metadata/practices")
def get_unique_practices(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    return get_opportunity_metadata("practices", db, current_user)

@router.get("/metadata/stages")
def get_unique_stages(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    return get_opportunity_metadata("stages", db, current_user)

@router.get("/metadata/statuses")
def get_unique_statuses(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    return get_opportunity_metadata("statuses", db, current_user)

@router.get("/document-categories")
def get_document_categories(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    categories = db.query(DocumentCategory).filter(DocumentCategory.is_active == True).all()
    return [{"category_id": c.category_id, "label_name": c.label_name} for c in categories]

class OpportunityResponse(BaseModel):
    id: str
    remote_id: Optional[str]
    name: str
    customer: str
    customer_name: Optional[str] = None
    practice: Optional[str] = "General"
    deal_value: float
    margin_percentage: Optional[float] = 0.0
    pat_margin: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    workflow_status: Optional[str]
    sales_stage: Optional[str] = "Discovery"
    geo: Optional[str] = "Global"
    close_date: Optional[str] = None
    sales_owner: Optional[str] = "N/A"
    assigned_practice_head: Optional[str] = None
    assigned_sales_head: Optional[str] = None
    assigned_sa: Optional[str] = None
    assigned_sp: Optional[str] = None
    assigned_finance: Optional[str] = None
    assigned_legal: Optional[str] = None
    win_probability: Optional[float] = 0
    overall_score: Optional[float] = 0
    version_no: Optional[int] = None
    row_id: Optional[str] = None
    gh_approval_status: Optional[str] = 'PENDING'
    ph_approval_status: Optional[str] = 'PENDING'
    sh_approval_status: Optional[str] = 'PENDING'
    legal_approval_status: Optional[str] = 'PENDING'
    finance_approval_status: Optional[str] = 'PENDING'
    assigned_practice_head_ids: List[str] = []
    assigned_sales_head_id: Optional[str] = None
    assigned_sa_ids: List[str] = []
    assigned_sp_id: Optional[str] = None
    assigned_finance_id: Optional[str] = None
    assigned_legal_id: Optional[str] = None
    combined_submission_ready: Optional[bool] = False
    recommendation: Optional[str] = None
    confidence_level: Optional[str] = None

class PaginatedOpportunityResponse(BaseModel):
    items: List[dict]
    total_count: int
    total_value: float = 0
    avg_win_prob: float = 0
    counts: Optional[dict] = None
    last_synced_at: Optional[datetime] = None

@router.get("/", response_model=PaginatedOpportunityResponse)
def get_all_opportunities(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    tab: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    region: Optional[str] = None,
    filters: Optional[str] = None, # JSON string: [{"id": "col", "value": "val"}]
    current_user: AppUser = Depends(get_current_user)
):
    try:
        print(f"DEBUG: Request params - role: {role}, user_id: {user_id}, tab: {tab}")
        # Extract logic to service but keep counts in router for now as they are very complex
        service_result = opportunity_service.get_paginated_opportunities_logic(
            db=db, page=page, limit=limit, search=search, tab=tab, 
            user_id=user_id, role=role, region=region, filters=filters,
            current_user_email=current_user.email
        )
        
        # 6. Tab Counts
        counts = opportunity_service.get_opportunity_counts_logic(
            db=db, user_id=user_id, role=role, 
            current_user_email=current_user.email
        )

        print(f"DEBUG: Query returned {len(service_result['items'])} records for {role}")
        return {
            "items": service_result["items"],
            "total_count": service_result["total_count"],
            "total_value": service_result["total_value"],
            "counts": counts,
            "last_synced_at": service_result["last_synced_at"]
        }
    except Exception as e:
        logger.error(f"Error fetching opportunities, invalid user id possible: {e}")
        return {
            "items": [],
            "total_count": 0,
            "total_value": 0,
            "counts": {},
            "last_synced_at": None
        }

@router.get("/{opp_id}", response_model=OpportunityResponse)
def get_opportunity_by_id(opp_id: str, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    res = opportunity_service.get_opportunity_by_id_logic(db, opp_id)
    if not res: raise HTTPException(404, "Opportunity not found")
    return res

# --- Action Endpoints ---

class StartAssessmentInput(BaseModel):
    sa_name: Optional[str] = None

@router.post("/{opp_id}/start-assessment")
def start_assessment(opp_id: str, data: StartAssessmentInput, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Not found")
    opp.workflow_status = "UNDER_ASSESSMENT"
    db.commit()
    return {"status": "success"}

class AssignRequest(BaseModel):
    assigned_practice_head_ids: Optional[List[str]] = None
    assigned_sales_head_id: Optional[str] = None
    assigned_sa_ids: Optional[List[str]] = None
    assigned_sp_id: Optional[str] = None
    assigned_finance_id: Optional[str] = None
    assigned_legal_id: Optional[str] = None

@router.post("/{opp_id}/assign")
def assign_role(opp_id: str, req: AssignRequest, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can assign pursuit team members.")
        
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    # Enforce validation: Pydantic Optional[str] already ensures these are strings not arrays
    # But we can add explicit logging or extra checks if needed.
    
    if req.assigned_practice_head_ids is not None:
        opp.assigned_practice_head_ids = req.assigned_practice_head_ids
    if req.assigned_sales_head_id is not None:
        opp.assigned_sales_head_id = req.assigned_sales_head_id
    if req.assigned_sa_ids is not None:
        opp.assigned_sa_ids = req.assigned_sa_ids
    if req.assigned_sp_id is not None:
        opp.assigned_sp_id = req.assigned_sp_id
    if req.assigned_finance_id is not None:
        opp.assigned_finance_id = req.assigned_finance_id
    if req.assigned_legal_id is not None:
        opp.assigned_legal_id = req.assigned_legal_id
        
    db.commit()
    return {"status": "success"}

class ApprovalRequest(BaseModel):
    role: str
    decision: str
    comment: Optional[str] = None
    user_id: str

@router.post("/{opp_id}/approve")
def process_approval_endpoint(opp_id: str, req: ApprovalRequest, db: Session = Depends(get_db), current_user: AppUser = Depends(require_role(["GH", "PH", "SH"]))):
    return handle_approval_action(
        db=db, 
        opp_id=opp_id, 
        role=req.role, 
        decision=req.decision, 
        comment=req.comment, 
        user_id=req.user_id
    )

class FinancialsUpdate(BaseModel):
    deal_value: Optional[float] = None
    pat_margin: Optional[float] = None

@router.patch("/{opp_id}/financials")
def update_financials(opp_id: str, data: FinancialsUpdate, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can modify financial data.")
    
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if data.deal_value is not None:
        opp.deal_value = data.deal_value
    if data.pat_margin is not None:
        opp.pat_margin = data.pat_margin
    
    db.commit()
    return {"status": "success", "deal_value": opp.deal_value, "pat_margin": opp.pat_margin}
