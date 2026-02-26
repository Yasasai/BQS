from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func
from typing import List, Optional, Any
from datetime import datetime, date
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import Opportunity, OpportunityAssignment, OppScoreVersion, Practice, AppUser, OppScoreSectionValue

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

@router.get("/metadata/regions")
def get_unique_regions(db: Session = Depends(get_db)):
    regions = db.query(Opportunity.geo).filter(Opportunity.geo.isnot(None), Opportunity.is_active == True).distinct().all()
    # Flatten list of tuples
    return [r[0] for r in regions if r[0]]

@router.get("/metadata/practices")
def get_unique_practices(db: Session = Depends(get_db)):
    practices = db.query(Practice.practice_name).join(Opportunity, Opportunity.primary_practice_id == Practice.practice_id).filter(Opportunity.is_active == True).distinct().all()
    return [p[0] for p in practices if p[0]]

@router.get("/metadata/stages")
def get_unique_stages(db: Session = Depends(get_db)):
    stages = db.query(Opportunity.stage).filter(Opportunity.stage.isnot(None), Opportunity.is_active == True).distinct().all()
    return [s[0] for s in stages if s[0]]

@router.get("/metadata/statuses")
def get_unique_statuses(db: Session = Depends(get_db)):
    # Combine workflow_status and some derived statuses if needed, 
    # but for now just unique workflow_status
    statuses = db.query(Opportunity.workflow_status).filter(Opportunity.workflow_status.isnot(None), Opportunity.is_active == True).distinct().all()
    return [s[0] for s in statuses if s[0]]

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
    filters: Optional[str] = None # JSON string: [{"id": "col", "value": "val"}]
):
    skip = (page - 1) * limit
    
    # 1. Base Query
    query = db.query(Opportunity).filter(Opportunity.is_active == True)
    
    # Outer joins for filtering by names
    query = query.outerjoin(AppUser, Opportunity.sales_owner_user_id == AppUser.user_id)
    query = query.outerjoin(Practice, Opportunity.primary_practice_id == Practice.practice_id)

    # 2. Search
    if search:
        st = f"%{search}%"
        query = query.filter(or_(
            Opportunity.opp_name.ilike(st),
            Opportunity.customer_name.ilike(st),
            Opportunity.opp_number.ilike(st)
        ))

    # 2.1 Region Filter (High Level)
    if region and region != 'All Regions':
        query = query.filter(Opportunity.geo == region)

    # 2.2 Column Filters (Excel-like)
    import json
    if filters:
        try:
            filter_list = json.loads(filters)
            for f in filter_list:
                col = f.get('id')
                val = f.get('value')
                if val is None: continue
                
                # Multi-select (tickboxes) usually send list of values
                if isinstance(val, list):
                    if not val: continue
                    if col == 'workflow_status' or col == 'status':
                        query = query.filter(Opportunity.workflow_status.in_(val))
                    elif col == 'geo' or col == 'Region':
                        query = query.filter(Opportunity.geo.in_(val))
                    elif col == 'sales_stage' or col == 'Sales Stage':
                        query = query.filter(Opportunity.stage.in_(val))
                    elif col == 'customer' or col == 'Account':
                        query = query.filter(Opportunity.customer_name.in_(val))
                    elif col == 'practice':
                        query = query.filter(Practice.practice_name.in_(val))
                    elif col == 'owner':
                        query = query.filter(AppUser.display_name.in_(val))
                    elif col == 'remote_id':
                         query = query.filter(Opportunity.opp_number.in_(val))
                    elif col == 'name':
                         query = query.filter(Opportunity.opp_name.in_(val))
                    elif col == 'account_owner':
                         # If we had a column for account owner, we'd filter it here
                         pass
                    elif col == 'win_probability':
                        # Special handling if needed, or just match the list
                        pass
                
                # Range filters (Amount) send {min, max}
                elif isinstance(val, dict):
                    if col == 'deal_value' or col == 'Amount':
                        vmin = val.get('min')
                        vmax = val.get('max')
                        if vmin is not None and vmin != '':
                            query = query.filter(Opportunity.deal_value >= float(vmin))
                        if vmax is not None and vmax != '':
                            query = query.filter(Opportunity.deal_value <= float(vmax))
                
                # Fallback for simple values
                else:
                    if col == 'name':
                        query = query.filter(Opportunity.opp_name.ilike(f"%{val}%"))
                    elif col == 'customer':
                        query = query.filter(Opportunity.customer_name.ilike(f"%{val}%"))
                    elif col == 'remote_id':
                        query = query.filter(Opportunity.opp_number.ilike(f"%{val}%"))
        except Exception as e:
            print(f"Filter error in backend: {e}")
            pass

    # 3. Role/Target filtering - Strictly enforced
    if role == 'PH':
        query = query.filter(Opportunity.assigned_practice_head_id == user_id) if user_id else query.filter(False)
    elif role == 'SH':
        query = query.filter(Opportunity.assigned_sales_head_id == user_id) if user_id else query.filter(False)
    elif role == 'GH':
        pass # Admin sees all
    elif role in ['SA', 'SP']:
        id_col = Opportunity.assigned_sa_id if role == 'SA' else Opportunity.assigned_sp_id
        query = query.filter(id_col == user_id) if user_id else query.filter(False)

    # 4. Tab filtering constants
    rev_stats = ['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']
    comp_stats = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']

    # 5. Tab specific logic
    tabs = tab.split(",") if tab else ["all"]
    tab_filters = []
    
    for t in tabs:
        if t == 'all':
            tab_filters.append(True)
        elif t in ['review', 'pending-review', 'submitted']:
            tab_filters.append(Opportunity.workflow_status.in_(rev_stats))
        elif t == 'completed':
            if role == 'PH':
                tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED'])))
            elif role == 'SH':
                tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED'])))
            elif role == 'GH':
                tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.gh_approval_status.in_(['APPROVED', 'REJECTED'])))
            elif role == 'SA':
                tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SA_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED'])))
            elif role == 'SP':
                tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SP_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED'])))
            else:
                tab_filters.append(Opportunity.workflow_status.in_(comp_stats))
        elif t == 'missing-ph' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.isnot(None)))
        elif t == 'missing-sh' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sales_head_id.is_(None), Opportunity.assigned_practice_head_id.isnot(None)))
        elif t == 'fully-assigned' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_practice_head_id.isnot(None), Opportunity.assigned_sales_head_id.isnot(None)))
        elif t == 'partially-assigned' and role == 'GH':
            # Missing PH or SH, but not both (which is unassigned)
            cond = or_(
                and_(Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.isnot(None)),
                and_(Opportunity.assigned_practice_head_id.isnot(None), Opportunity.assigned_sales_head_id.is_(None))
            )
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), cond))
        elif t in ['action-required', 'unassigned', 'needs-action']:
            # Action Required means: Outstanding task for THIS role
            tf = (or_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.is_(None)))
            if role == 'PH': tf = and_(tf, Opportunity.assigned_sa_id.is_(None))
            elif role == 'SH': tf = and_(tf, Opportunity.assigned_sp_id.is_(None))
            elif role == 'GH':
                if t == 'unassigned': tf = and_(tf, Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.is_(None))
                else: tf = and_(tf, or_(Opportunity.assigned_practice_head_id.is_(None), Opportunity.assigned_sales_head_id.is_(None)))
            elif role in ['SA', 'SP']:
                tf = and_(tf, or_(Opportunity.workflow_status.notin_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT'] + rev_stats + comp_stats), Opportunity.workflow_status.is_(None)))
            tab_filters.append(tf)
        elif t == 'in-progress':
            tf = (or_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.is_(None)))
            if role == 'PH': tf = and_(tf, Opportunity.assigned_sa_id.isnot(None))
            elif role == 'SH': tf = and_(tf, Opportunity.assigned_sp_id.isnot(None))
            elif role in ['SA', 'SP']: tf = and_(tf, Opportunity.workflow_status.in_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT']))
            else: tf = and_(tf, or_(Opportunity.assigned_practice_head_id.isnot(None), Opportunity.assigned_sales_head_id.isnot(None)))
            tab_filters.append(tf)

    if tab_filters:
        query = query.filter(or_(*tab_filters))

    # 6. Pagination and Metrics
    total_count = query.count()
    pipeline_value = db.query(func.sum(Opportunity.deal_value)).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).scalar() or 0
    
    # Role-based Tab Counts (Dynamic)
    base_role = db.query(Opportunity).filter(Opportunity.is_active == True)
    if role == 'PH':
        base_role = base_role.filter(Opportunity.assigned_practice_head_id == user_id) if user_id else base_role.filter(False)
    elif role == 'SH':
        base_role = base_role.filter(Opportunity.assigned_sales_head_id == user_id) if user_id else base_role.filter(False)
    elif role in ['SA', 'SP']:
        id_col = Opportunity.assigned_sa_id if role == 'SA' else Opportunity.assigned_sp_id
        base_role = base_role.filter(id_col == user_id) if user_id else base_role.filter(False)

    if role == 'PH':
        f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED']))).count()
        f_rev = base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count()
        
        # Action Required for PH: Missing Assignment OR Pending Approval
        f_act_assign = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sa_id.is_(None))).count()
        f_act_approve = base_role.filter(and_(Opportunity.workflow_status.in_(rev_stats), Opportunity.ph_approval_status == 'PENDING')).count()
        f_act = f_act_assign + f_act_approve
        
        f_prog = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sa_id.isnot(None))).count()
        counts = {
            "all": base_role.count(),
            "action-required": f_act,
            "in-progress": f_prog,
            "review": f_rev,
            "completed": f_comp
        }
    elif role == 'SH':
        f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED']))).count()
        f_rev = base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count()
        
        # Action Required for SH: Missing Assignment OR Pending Approval
        f_act_assign = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sp_id.is_(None))).count()
        f_act_approve = base_role.filter(and_(Opportunity.workflow_status.in_(rev_stats), Opportunity.sh_approval_status == 'PENDING')).count()
        f_act = f_act_assign + f_act_approve
        
        f_prog = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sp_id.isnot(None))).count()
        counts = {
            "all": base_role.count(),
            "action-required": f_act,
            "in-progress": f_prog,
            "review": f_rev,
            "completed": f_comp
        }
    elif role in ['SA', 'SP']:
        # Dual Visibility for Executors
        if role == 'SA':
            f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SA_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED']))).count()
        else:
            f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SP_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED']))).count()
            
        f_sub = base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count()
        f_prog = base_role.filter(Opportunity.workflow_status.in_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT'])).count()
        f_act = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats + ['UNDER_ASSESSMENT', 'IN_ASSESSMENT']), Opportunity.workflow_status.isnot(None))).count()
        counts = {
            "all": base_role.count(),
            "action-required": f_act,
            "needs-action": f_act,
            "in-progress": f_prog,
            "submitted": f_sub,
            "completed": f_comp
        }
    else:
        # GH (Global Head) counts
        f_rev = Opportunity.workflow_status.in_(rev_stats)
        f_comp = or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.gh_approval_status.in_(['APPROVED', 'REJECTED']))
        f_open = and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.isnot(None))
        
        f_no_ph = Opportunity.assigned_practice_head_id.is_(None)
        f_no_sh = Opportunity.assigned_sales_head_id.is_(None)
        
        counts = {
            "all": base_role.count(),
            "unassigned": base_role.filter(and_(f_open, f_no_ph, f_no_sh)).count(),
            "missing-ph": base_role.filter(and_(f_open, f_no_ph, ~f_no_sh)).count(),
            "missing-sh": base_role.filter(and_(f_open, ~f_no_ph, f_no_sh)).count(),
            "partially-assigned": base_role.filter(and_(f_open, or_(and_(f_no_ph, ~f_no_sh), and_(~f_no_ph, f_no_sh)))).count(),
            "fully-assigned": base_role.filter(and_(f_open, ~f_no_ph, ~f_no_sh)).count(),
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
        
    # Query latest sync
    last_sync = db.query(func.max(Opportunity.local_last_synced_at)).scalar()

    return {
        "items": results,
        "total_count": total_count,
        "total_value": pipeline_value,
        "counts": counts,
        "last_synced_at": last_sync
    }

@router.get("/{opp_id}", response_model=OpportunityResponse)
def get_opportunity_by_id(opp_id: str, db: Session = Depends(get_db)):
    o = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not o: raise HTTPException(404, "Opportunity not found")

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
    
    # Check if any actual scores have been entered
    has_ratings = False
    if latest_score:
        has_ratings = db.query(OppScoreSectionValue).filter(
            OppScoreSectionValue.score_version_id == latest_score.score_version_id,
            OppScoreSectionValue.score > 0
        ).first() is not None

    status = o.workflow_status
    if not status or status in ['OPEN', 'ASSIGNED_TO_SA', 'ASSIGNED_TO_SP', 'UNDER_ASSESSMENT']:
        if latest_score:
            if latest_score.status == 'SUBMITTED': 
                status = "SUBMITTED"
            elif latest_score.status in ['APPROVED', 'REJECTED']:
                status = latest_score.status
            elif has_ratings:
                status = "UNDER_ASSESSMENT"
            elif o.assigned_sa_id or o.assigned_sp_id:
                status = "ASSIGNED"
            else:
                status = "NEW"
        else:
            if o.assigned_sa_id or o.assigned_sp_id:
                status = "ASSIGNED"
            else:
                status = "NEW"
    
    return {
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
    }

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

    # Reset submission flags for the active version if an executor is being assigned
    if req.role in ['SA', 'SP']:
        latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        if latest:
            if req.role == 'SA': latest.sa_submitted = False
            if req.role == 'SP': latest.sp_submitted = False
            # Re-open if it was marked as submitted
            if latest.status == 'SUBMITTED': latest.status = 'UNDER_ASSESSMENT'
        
        # Ensure workflow status reflects that work is pending
        if not opp.workflow_status or opp.workflow_status in ['READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW', 'SUBMITTED']:
            opp.workflow_status = "UNDER_ASSESSMENT"

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
    
    # Persistent Audit Log: Update latest version with decision
    latest_ver = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    if latest_ver:
        decision_label = f"[{req.role} {decision}]"
        current_comment = latest_ver.summary_comment or ""
        if req.comment:
            latest_ver.summary_comment = f"{decision_label}: {req.comment}\n---\n{current_comment}"
        else:
            latest_ver.summary_comment = f"{decision_label}: No comment provided.\n---\n{current_comment}"
        
        # If it's a final rejection, mark the version
        if decision == 'REJECTED':
            latest_ver.status = 'REJECTED'
        elif (opp.gh_approval_status == 'APPROVED' and opp.ph_approval_status == 'APPROVED' and opp.sh_approval_status == 'APPROVED'):
            latest_ver.status = 'APPROVED'

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
