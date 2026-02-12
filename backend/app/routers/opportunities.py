from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func
from typing import List, Optional, Any
from datetime import datetime, date
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import Opportunity, OpportunityAssignment, OppScoreVersion, Practice, AppUser

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

class OpportunityResponse(BaseModel):
    id: str
    remote_id: Optional[str]
    name: str
    customer: str
    practice: Optional[str] = "General"
    deal_value: float
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
    win_probability: Optional[float] = 0
    version_no: Optional[int] = None
    row_id: Optional[str] = None
    gh_approval_status: Optional[str] = 'PENDING'
    ph_approval_status: Optional[str] = 'PENDING'
    sh_approval_status: Optional[str] = 'PENDING'
    assigned_practice_head_id: Optional[str] = None
    assigned_sales_head_id: Optional[str] = None
    combined_submission_ready: Optional[bool] = False

class PaginatedOpportunityResponse(BaseModel):
    items: List[dict]
    total_count: int
    total_value: float = 0
    avg_win_prob: float = 0
    counts: Optional[dict] = None

@router.get("/", response_model=PaginatedOpportunityResponse)
def get_all_opportunities(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    tab: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None
):
    skip = (page - 1) * limit
    
    # 1. Base Query
    query = db.query(Opportunity).filter(Opportunity.is_active == True)

    # 2. Search
    if search:
        st = f"%{search}%"
        query = query.filter(or_(
            Opportunity.opp_name.ilike(st),
            Opportunity.customer_name.ilike(st),
            Opportunity.opp_number.ilike(st)
        ))

    # 3. Role/Target filtering (Safety Hatch for demo items)
    targets = ['RetailCo', 'Acme']
    safety_hatch = or_(*[Opportunity.opp_name.ilike(f'%{t}%') for t in targets])

    if role == 'PH' and user_id:
        query = query.filter(or_(Opportunity.assigned_practice_head_id == user_id, safety_hatch))
    elif role == 'SH' and user_id:
        query = query.filter(or_(Opportunity.assigned_sales_head_id == user_id, safety_hatch))
    elif role == 'GH':
        pass # Admin sees all
    elif role in ['SA', 'SP'] and user_id:
        id_col = Opportunity.assigned_sa_id if role == 'SA' else Opportunity.assigned_sp_id
        query = query.filter(id_col == user_id)

    # 4. Tab filtering constants
    rev_stats = ['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']
    comp_stats = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']

    # 5. Tab specific logic
    if tab in ['review', 'pending-review']:
        query = query.filter(Opportunity.workflow_status.in_(rev_stats))
        if role in ['PH', 'SH']:
            query = query.filter(Opportunity.workflow_status != 'PENDING_GH_APPROVAL')
    elif tab == 'completed':
        query = query.filter(Opportunity.workflow_status.in_(comp_stats))
    elif tab == 'missing-ph' and role == 'GH':
        query = query.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.isnot(None)))
    elif tab == 'missing-sh' and role == 'GH':
        query = query.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sales_head_id.is_(None), Opportunity.assigned_practice_head_id.isnot(None)))
    elif tab in ['action-required', 'unassigned']:
        query = query.filter(Opportunity.workflow_status.notin_(comp_stats))
        if role == 'PH': query = query.filter(Opportunity.assigned_sa_id.is_(None))
        elif role == 'SH': query = query.filter(Opportunity.assigned_sp_id.is_(None))
        elif role == 'GH':
            # GH "Unassigned" means absolute zero assignments
            query = query.filter(and_(Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.is_(None)))
    elif tab == 'in-progress':
        # Anything with at least one assignment but not finalized
        query = query.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), or_(Opportunity.assigned_practice_head_id.isnot(None), Opportunity.assigned_sales_head_id.isnot(None))))

    # 6. Pagination and Metrics
    total_count = query.count()
    pipeline_value = db.query(func.sum(Opportunity.deal_value)).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).scalar() or 0
    
    # Role-based Tab Counts (Dynamic)
    base_role = db.query(Opportunity).filter(Opportunity.is_active == True)
    if role == 'PH' and user_id: base_role = base_role.filter(or_(Opportunity.assigned_practice_head_id == user_id, safety_hatch))
    elif role == 'SH' and user_id: base_role = base_role.filter(or_(Opportunity.assigned_sales_head_id == user_id, safety_hatch))
    elif role in ['SA', 'SP'] and user_id: base_role = base_role.filter((Opportunity.assigned_sa_id if role == 'SA' else Opportunity.assigned_sp_id) == user_id)

    if role == 'PH':
        f_comp = Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED'])
        # Fast track (PENDING_GH_APPROVAL) bypasses PH
        f_rev = and_(~f_comp, Opportunity.workflow_status.in_(rev_stats), Opportunity.workflow_status != 'PENDING_GH_APPROVAL')
        f_act = and_(~f_comp, ~f_rev, Opportunity.assigned_sa_id.is_(None))
        f_prog = and_(~f_comp, ~f_rev, Opportunity.assigned_sa_id.isnot(None))
        counts = {
            "all": base_role.count(),
            "action-required": base_role.filter(f_act).count(),
            "in-progress": base_role.filter(f_prog).count(),
            "review": base_role.filter(f_rev).count(),
            "completed": base_role.filter(f_comp).count()
        }
    elif role == 'SH':
        f_comp = Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED'])
        # Fast track (PENDING_GH_APPROVAL) bypasses SH
        f_rev = and_(~f_comp, Opportunity.workflow_status.in_(rev_stats), Opportunity.workflow_status != 'PENDING_GH_APPROVAL')
        f_act = and_(~f_comp, ~f_rev, Opportunity.assigned_sp_id.is_(None))
        f_prog = and_(~f_comp, ~f_rev, Opportunity.assigned_sp_id.isnot(None))
        counts = {
            "all": base_role.count(),
            "action-required": base_role.filter(f_act).count(),
            "in-progress": base_role.filter(f_prog).count(),
            "review": base_role.filter(f_rev).count(),
            "completed": base_role.filter(f_comp).count()
        }
    else:
        # GH (Global Head) counts
        f_rev = Opportunity.workflow_status.in_(rev_stats)
        f_comp = Opportunity.workflow_status.in_(comp_stats)
        f_open = and_(~f_rev, ~f_comp)
        
        f_no_ph = Opportunity.assigned_practice_head_id.is_(None)
        f_no_sh = Opportunity.assigned_sales_head_id.is_(None)
        
        counts = {
            "all": base_role.count(),
            "unassigned": base_role.filter(and_(f_open, f_no_ph, f_no_sh)).count(),
            "missing-ph": base_role.filter(and_(f_open, f_no_ph, ~f_no_sh)).count(),
            "missing-sh": base_role.filter(and_(f_open, ~f_no_ph, f_no_sh)).count(),
            "review": base_role.filter(f_rev).count(),
            "pending-review": base_role.filter(f_rev).count(),
            "completed": base_role.filter(f_comp).count()
        }
        counts['in-progress'] = base_role.filter(and_(f_open, or_(~f_no_ph, ~f_no_sh))).count()
        counts['action-required'] = counts['unassigned'] + counts['missing-ph'] + counts['missing-sh']

    # 7. Execute Query & Format results ( restoring Detailed data)
    opps = query.order_by(desc(Opportunity.crm_last_updated_at)).offset(skip).limit(limit).all()
    results = []
    
    for o in opps:
        # Resolve Practice
        practice_name = "General"
        if o.primary_practice_id:
            practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
            if practice: practice_name = practice.practice_name
        
        # Resolve Owner/Names
        def gname(uid):
            if not uid: return None
            u = db.query(AppUser).filter(AppUser.user_id == uid).first()
            return u.display_name if u else uid

        sales_owner_name = gname(o.sales_owner_user_id) or "N/A"
        
        # Resolve Latest Score & More Logical Status
        latest_score = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == o.opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        
        status = o.workflow_status
        if not status or status == 'OPEN':
            if latest_score:
                if latest_score.status == 'SUBMITTED': status = "SUBMITTED_FOR_REVIEW"
                elif latest_score.status == 'DRAFT': status = "UNDER_ASSESSMENT"
                else: status = latest_score.status
            else:
                status = "NEW"
        
        results.append({
            "id": o.opp_id,
            "row_id": o.opp_id,
            "remote_id": o.opp_number or "N/A",
            "name": o.opp_name,
            "customer": o.customer_name,
            "practice": practice_name,
            "deal_value": o.deal_value or 0.0,
            "currency": o.currency or "USD",
            "workflow_status": status,
            "sales_stage": o.stage or "Qualifying",
            "geo": o.geo or "Global",
            "close_date": o.close_date.strftime("%Y-%m-%d") if o.close_date else None,
            "sales_owner": sales_owner_name,
            "assigned_practice_head": gname(o.assigned_practice_head_id),
            "assigned_sales_head": gname(o.assigned_sales_head_id),
            "assigned_sa": gname(o.assigned_sa_id),
            "assigned_sp": gname(o.assigned_sp_id),
            "win_probability": latest_score.overall_score if latest_score else 0,
            "version_no": latest_score.version_no if latest_score else None,
            "gh_approval_status": o.gh_approval_status or 'PENDING',
            "ph_approval_status": o.ph_approval_status or 'PENDING',
            "sh_approval_status": o.sh_approval_status or 'PENDING',
            "assigned_practice_head_id": o.assigned_practice_head_id,
            "assigned_sales_head_id": o.assigned_sales_head_id,
            "combined_submission_ready": o.combined_submission_ready or False
        })
        
    return {"items": results, "total_count": total_count, "total_value": pipeline_value, "counts": counts}

# --- Action Endpoints ---

class StartAssessmentInput(BaseModel):
    sa_name: Optional[str] = None

@router.post("/{opp_id}/start-assessment")
def start_assessment(opp_id: str, data: StartAssessmentInput, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Not found")
    opp.workflow_status = "UNDER_ASSESSMENT"
    db.commit()
    return {"status": "success"}

class AssignRequest(BaseModel):
    role: str
    user_id: str
    assigned_by: str

@router.post("/{opp_id}/assign")
def assign_role(opp_id: str, req: AssignRequest, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Not found")
    if req.role == 'PH': opp.assigned_practice_head_id = req.user_id
    elif req.role == 'SH': opp.assigned_sales_head_id = req.user_id
    elif req.role == 'SA': opp.assigned_sa_id = req.user_id
    elif req.role == 'SP': opp.assigned_sp_id = req.user_id
    db.commit()
    return {"status": "success"}

class ApprovalRequest(BaseModel):
    role: str
    decision: str
    comment: Optional[str] = None
    user_id: str

@router.post("/{opp_id}/approve")
def process_approval(opp_id: str, req: ApprovalRequest, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Not found")
    decision = req.decision.upper()
    if 'APPROVE' in decision: decision = 'APPROVED'
    if 'REJECT' in decision: decision = 'REJECTED'
    
    if req.role == 'GH':
        opp.gh_approval_status = decision
        # Special Rule: Fast Track (3.5 to 4.0)
        # If it was pending GH approval specifically, and GH approves, finalize it immediately.
        if opp.workflow_status == 'PENDING_GH_APPROVAL' and decision == 'APPROVED':
            opp.workflow_status = 'APPROVED'
            db.commit()
            return {"status": "success", "message": "Fast-track approval completed by GH"}
    elif req.role == 'PH': opp.ph_approval_status = decision
    elif req.role == 'SH': opp.sh_approval_status = decision
    
    if decision == 'REJECTED':
        opp.workflow_status = 'REJECTED'
    elif (opp.gh_approval_status == 'APPROVED' and opp.ph_approval_status == 'APPROVED' and opp.sh_approval_status == 'APPROVED'):
        opp.workflow_status = 'APPROVED'
    else:
        # If it was fast track and rejected, it's already caught by REJECTED block.
        # Otherwise, keep it moving.
        if opp.workflow_status != 'PENDING_GH_APPROVAL':
            opp.workflow_status = 'PENDING_FINAL_APPROVAL'
    
    db.commit()
    return {"status": "success"}
