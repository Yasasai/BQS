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
    practice: Optional[str]
    deal_value: float
    currency: Optional[str]
    workflow_status: Optional[str]
    sales_stage: Optional[str]
    geo: Optional[str]
    close_date: Optional[str]
    sales_owner: Optional[str]
    assigned_practice_head: Optional[str]
    assigned_sa: Optional[str]
    win_probability: Optional[float] = 0
    version_no: Optional[int] = None
    row_id: Optional[str] = None # Unique ID for table row (e.g. oppid_vX)
    
    # New Multi-Stage Fields
    gh_approval_status: Optional[str] = 'PENDING'
    ph_approval_status: Optional[str] = 'PENDING'
    sh_approval_status: Optional[str] = 'PENDING'
    assigned_practice_head_id: Optional[str] = None
    assigned_sales_head_id: Optional[str] = None
    assigned_practice_head: Optional[str] = None
    assigned_sales_head: Optional[str] = None
    assigned_sa: Optional[str] = None
    assigned_sp: Optional[str] = None
    combined_submission_ready: Optional[bool] = False


class PaginatedOpportunityResponse(BaseModel):
    items: List[OpportunityResponse]
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
    # Calculate skip
    skip = (page - 1) * limit

    # Build Query
    query = db.query(Opportunity).filter(Opportunity.is_active == True).order_by(desc(Opportunity.crm_last_updated_at))

    # --- Role-Based Filtering ---
    if role == 'PH' and user_id:
        query = query.filter(Opportunity.assigned_practice_head_id == user_id)
    elif role == 'SH' and user_id:
        query = query.filter(Opportunity.assigned_sales_head_id == user_id)
    # GH sees everything if they ask for 'all', but primarily focused on assignments
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
             (Opportunity.opp_name.ilike(search_term)) | 
             (Opportunity.customer_name.ilike(search_term)) |
             (Opportunity.opp_number.ilike(search_term))
        )

    from sqlalchemy import or_, and_

    # --- Role-Based Filtering Logic ---
    
    # 1. Base Filter: Filter by Role & User ID (except for GH/Admin)
    if role == 'PH' and user_id:
        query = query.filter(Opportunity.assigned_practice_head_id == user_id)
    elif role == 'SH' and user_id:
        query = query.filter(Opportunity.assigned_sales_head_id == user_id)
    elif role == 'SA' and user_id:
        query = query.filter(Opportunity.assigned_sa_id == user_id)
    elif role == 'SP' and user_id:
        query = query.filter(Opportunity.assigned_sp_id == user_id)
    # GH gets to see everything by default
    
    # 2. Tab-Based Filtering
    if role == 'GH':
        if tab == 'unassigned':
            query = query.filter(or_(Opportunity.workflow_status.in_(['NEW', 'OPEN', '']), Opportunity.workflow_status.is_(None)))
        elif tab in ['pending-review', 'review']:
            query = query.filter(
                Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
                Opportunity.gh_approval_status == 'PENDING'
            )
        elif tab == 'completed':
            query = query.filter(Opportunity.workflow_status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']))
    
    elif role == 'PH':
        if tab == 'action-required':
            # Needs to assign SA
            # Logic: Broader check - if I am assigned (implied by base filter) and SA is NOT assigned, and opp is allowed (not closed).
            query = query.filter(
                Opportunity.assigned_sa_id.is_(None),
                or_(
                    Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']),
                    Opportunity.workflow_status.is_(None)
                )
            )
        elif tab == 'in-progress':
            # Include standard in-progress statuses AND cases where I assigned SA but overall status isn't updated yet
            query = query.filter(
                or_(
                    Opportunity.workflow_status.in_(['IN_ASSESSMENT', 'EXECUTORS_ASSIGNED', 'UNDER_ASSESSMENT']),
                    and_(
                        Opportunity.assigned_sa_id.isnot(None),
                        Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN', None, ''])
                    )
                )
            )
        elif tab == 'review':
            # Needs to review assessment
            query = query.filter(
                Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
                Opportunity.ph_approval_status == 'PENDING'
            )
        elif tab == 'completed':
             query = query.filter(Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED']))

    elif role == 'SH':
        if tab == 'action-required':
            # Needs to assign SP
            query = query.filter(
                Opportunity.assigned_sp_id.is_(None),
                or_(
                    Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']),
                    Opportunity.workflow_status.is_(None)
                )
            )
        elif tab == 'in-progress':
             # Include standard in-progress statuses AND cases where I assigned SP but overall status isn't updated yet
             query = query.filter(
                 or_(
                     Opportunity.workflow_status.in_(['IN_ASSESSMENT', 'EXECUTORS_ASSIGNED', 'UNDER_ASSESSMENT']),
                     and_(
                         Opportunity.assigned_sp_id.isnot(None),
                         Opportunity.workflow_status.in_(['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED', 'NEW', 'OPEN', None, ''])
                     )
                 )
             )
        elif tab == 'review':
             # Needs to review assessment
            query = query.filter(
                Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
                Opportunity.sh_approval_status == 'PENDING'
            )
        elif tab == 'completed':
             query = query.filter(Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED']))

    elif role == 'SA':
        # Base Query: Active & Assigned to me as SA
        base_query = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.assigned_sa_id == user_id
        )
        
        # 1. Assigned (Not started yet)
        filter_assigned = and_(
            Opportunity.workflow_status.notin_(['IN_ASSESSMENT', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        # 2. In Progress
        filter_in_progress = (Opportunity.workflow_status == 'IN_ASSESSMENT')
        
        # 3. Submitted (Under Review)
        filter_submitted = (Opportunity.workflow_status == 'UNDER_REVIEW')
        
        # 4. Completed
        filter_completed = Opportunity.workflow_status.in_(['APPROVED', 'REJECTED'])

        if tab == 'assigned':
            query = query.filter(filter_assigned)
        elif tab == 'in-progress':
            query = query.filter(filter_in_progress)
        elif tab == 'submitted':
            query = query.filter(filter_submitted)
        elif tab == 'completed':
             query = query.filter(filter_completed)

        # Tab Counts
        tab_counts = {
            "assigned": base_query.filter(filter_assigned).count(),
            "in-progress": base_query.filter(filter_in_progress).count(),
            "submitted": base_query.filter(filter_submitted).count(),
            "completed": base_query.filter(filter_completed).count()
        }

    elif role == 'SP':
        # Base Query: Active & Assigned to me as SP
        base_query = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.assigned_sp_id == user_id
        )
        
        # 1. Assigned
        filter_assigned = and_(
            Opportunity.workflow_status.notin_(['IN_ASSESSMENT', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        # 2. In Progress
        filter_in_progress = (Opportunity.workflow_status == 'IN_ASSESSMENT')
        
        # 3. Submitted
        filter_submitted = (Opportunity.workflow_status == 'UNDER_REVIEW')
        
        # 4. Completed
        filter_completed = Opportunity.workflow_status.in_(['APPROVED', 'REJECTED'])

        if tab == 'assigned':
            query = query.filter(filter_assigned)
        elif tab == 'in-progress':
            query = query.filter(filter_in_progress)
        elif tab == 'submitted':
            query = query.filter(filter_submitted)
        elif tab == 'completed':
             query = query.filter(filter_completed)

        # Tab Counts
        tab_counts = {
            "assigned": base_query.filter(filter_assigned).count(),
            "in-progress": base_query.filter(filter_in_progress).count(),
            "submitted": base_query.filter(filter_submitted).count(),
            "completed": base_query.filter(filter_completed).count()
        }
    
    # Fallback for legacy calls or specific tabs not covered above
    if not role or role not in ['GH', 'PH', 'SH', 'SA', 'SP']:
        if tab == 'unassigned':
            query = query.filter(or_(Opportunity.workflow_status.in_(['NEW', 'OPEN', '']), Opportunity.workflow_status.is_(None)))
        elif tab == 'assigned':
             query = query.filter(Opportunity.workflow_status.in_(['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT', 'HEADS_ASSIGNED', 'EXECUTORS_ASSIGNED', 'IN_ASSESSMENT']))
        elif tab == 'review':
             query = query.filter(Opportunity.workflow_status.in_(['SUBMITTED_FOR_REVIEW', 'SUBMITTED', 'UNDER_REVIEW']))
        elif tab == 'completed':
            query = query.filter(Opportunity.workflow_status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']))

    # Note: 'all' or no tab returns everything unfiltered (subject to role-base base filter).

    # Get Metrics Across Full Filtered Query (Before Pagination)
    from sqlalchemy import func
    total_count = query.count()
    
    metrics = db.query(
        func.sum(Opportunity.deal_value).label("total_val")
    ).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).first()
    
    pipeline_value = metrics.total_val if metrics and metrics.total_val else 0
    
    
    # --- Role-Based Tab Counts ---
    tab_counts = {}

    if role == 'GH':
        total_all = db.query(Opportunity).filter(Opportunity.is_active == True).count()
        count_unassigned = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            or_(Opportunity.workflow_status.in_(['NEW', 'OPEN', '']), Opportunity.workflow_status.is_(None))
        ).count()
        count_review = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
            Opportunity.gh_approval_status == 'PENDING'
        ).count()
        count_completed = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.workflow_status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        ).count()

        tab_counts = {
            "all": total_all,
            "unassigned": count_unassigned,
            "pending-review": count_review, 
            "review": count_review, # Alias for frontend compatibility
            "completed": count_completed
        }

    elif role == 'PH' and user_id:
        # Base Query: Active & Assigned to user
        base_query = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.assigned_practice_head_id == user_id
        )
        
        # Define Filters (Waterfall Logic)
        
        # 1. Completed: PH has made a decision
        filter_completed = Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED'])
        
        filter_review = and_(
             ~filter_completed,
             Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
             Opportunity.ph_approval_status == 'PENDING'
        )
        
        # 3. In Progress: SA is Assigned (and not in Review/Completed)
        # Logic: Not completed, Not in Review, SA IS assigned, and Not Closed
        filter_in_progress = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sa_id.isnot(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        # 4. Action Required: SA is NOT Assigned (and not closed)
        # Logic: All remaining active opportunities
        filter_action = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sa_id.is_(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )

        # Apply Tab Filter
        if tab == 'completed':
            query = query.filter(filter_completed)
        elif tab == 'review':
             query = query.filter(filter_review)
        elif tab == 'in-progress':
             query = query.filter(filter_in_progress)
        elif tab == 'action-required':
             query = query.filter(filter_action)

        # Calculate Counts
        tab_counts = {
            "completed": base_query.filter(filter_completed).count(),
            "review": base_query.filter(filter_review).count(),
            "in-progress": base_query.filter(filter_in_progress).count(),
            "action-required": base_query.filter(filter_action).count()
        }

    elif role == 'SH' and user_id:
        # Base Query: Active & Assigned to user
        base_query = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.assigned_sales_head_id == user_id
        )
        
        # Define Filters (Waterfall Logic)
        
        # 1. Completed
        filter_completed = Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED'])
        
        filter_review = and_(
             ~filter_completed,
             Opportunity.workflow_status.in_(['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED']),
             Opportunity.sh_approval_status == 'PENDING'
        )
        
        # 3. In Progress: SP Assigned
        filter_in_progress = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sp_id.isnot(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        
        # 4. Action Required: SP Not Assigned
        filter_action = and_(
            ~filter_completed,
            ~filter_review,
            Opportunity.assigned_sp_id.is_(None),
            Opportunity.workflow_status.notin_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )

        # Apply Tab Filter
        if tab == 'completed':
            query = query.filter(filter_completed)
        elif tab == 'review':
             query = query.filter(filter_review)
        elif tab == 'in-progress':
             query = query.filter(filter_in_progress)
        elif tab == 'action-required':
             query = query.filter(filter_action)

        # Calculate Counts
        tab_counts = {
            "completed": base_query.filter(filter_completed).count(),
            "review": base_query.filter(filter_review).count(),
            "in-progress": base_query.filter(filter_in_progress).count(),
            "action-required": base_query.filter(filter_action).count()
        }
        
    elif role in ['SA', 'SP'] and user_id:
        # Determine correct ID column
        id_col = Opportunity.assigned_sa_id if role == 'SA' else Opportunity.assigned_sp_id
        
        base_query = db.query(Opportunity).filter(
            Opportunity.is_active == True, 
            id_col == user_id
        )
        
        count_assigned = base_query.filter(Opportunity.workflow_status == 'EXECUTORS_ASSIGNED').count()
        count_in_progress = base_query.filter(Opportunity.workflow_status == 'IN_ASSESSMENT').count()
        count_submitted = base_query.filter(Opportunity.workflow_status == 'UNDER_REVIEW').count()
        count_completed = base_query.filter(Opportunity.workflow_status.in_(['APPROVED', 'REJECTED'])).count()
        
        tab_counts = {
            "assigned": count_assigned,
            "in-progress": count_in_progress,
            "submitted": count_submitted,
            "completed": count_completed
        }
    
    # Apply Pagination
    print(f"🔍 Querying opportunities - Tab: {tab}, Page: {page}, Limit: {limit}, Search: {search}")
    opps = query.offset(skip).limit(limit).all()
    print(f"📊 Found {len(opps)} opportunities (Total: {total_count})")
    
    results = []
    
    if tab == 'completed':
        # SPECIAL CASE: Show finalized Version records, not just Opportunities
        v_query = db.query(OppScoreVersion).join(Opportunity).filter(
            Opportunity.is_active == True,
            OppScoreVersion.status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        )
        if search:
            search_term = f"%{search}%"
            v_query = v_query.filter(
                (Opportunity.opp_name.ilike(search_term)) | 
                (Opportunity.customer_name.ilike(search_term)) |
                (Opportunity.opp_number.ilike(search_term))
            )
        
        total_count = v_query.count()
        # Metrics for versions
        metrics = db.query(func.sum(Opportunity.deal_value)).select_from(OppScoreVersion).join(Opportunity).filter(
             OppScoreVersion.status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
        ).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).first()
        pipeline_value = metrics[0] if metrics and metrics[0] else 0

        versions = v_query.order_by(desc(OppScoreVersion.submitted_at)).offset(skip).limit(limit).all()
        
        for v in versions:
            o = v.opportunity
            practice_name = "General"
            if o.primary_practice_id:
                practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
                if practice: practice_name = practice.practice_name
            
            # Resolve Assigned SA for this version if possible, or use current
            assigned_sa_name = None
            if v.created_by_user_id:
                sa_user = db.query(AppUser).filter(AppUser.user_id == v.created_by_user_id).first()
                if sa_user: assigned_sa_name = sa_user.display_name

            results.append({
                "id": o.opp_id,
                "row_id": f"{o.opp_id}_v{v.version_no}",
                "remote_id": o.opp_number or "N/A",
                "name": f"{o.opp_name} (v{v.version_no})",
                "customer": o.customer_name,
                "practice": practice_name,
                "deal_value": o.deal_value or 0.0,
                "currency": o.currency or "USD",
                "workflow_status": v.status,
                "sales_stage": o.stage or "Prospecting",
                "geo": o.geo or "Global",
                "close_date": o.close_date.strftime("%Y-%m-%d") if o.close_date else None,
                "sales_owner": "N/A", # Optional lookup 
                "assigned_practice_head": "N/A",
                "assigned_sa": assigned_sa_name,
                "win_probability": v.overall_score or 0,
                "version_no": v.version_no,
                "gh_approval_status": o.gh_approval_status or 'PENDING',
                "ph_approval_status": o.ph_approval_status or 'PENDING',
                "sh_approval_status": o.sh_approval_status or 'PENDING',
                "assigned_practice_head_id": o.assigned_practice_head_id,
                "assigned_sales_head_id": o.assigned_sales_head_id,
                "combined_submission_ready": o.combined_submission_ready or False
            })
    else:
        # Standard Opportunity-based view
        opps = query.offset(skip).limit(limit).all()
        for o in opps:
            # Determine Status
            status = "NEW"
            win_prob = 0
            version_no = None
            practice_name = "General"
            sales_owner_name = "Unknown"
            c_date_str = o.close_date.strftime("%Y-%m-%d") if o.close_date else None

            # Resolve Practice
            if o.primary_practice_id:
                practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
                if practice: practice_name = practice.practice_name

            # Resolve Sales Owner
            if o.sales_owner_user_id:
                owner = db.query(AppUser).filter(AppUser.user_id == o.sales_owner_user_id).first()
                if owner: sales_owner_name = owner.display_name

            # Resolve Assigned Names from Model Fields
            def get_user_name(uid):
                if not uid: return None
                u = db.query(AppUser).filter(AppUser.user_id == uid).first()
                return u.display_name if u else None

            ph_name = get_user_name(o.assigned_practice_head_id)
            sh_name = get_user_name(o.assigned_sales_head_id)
            sa_name = get_user_name(o.assigned_sa_id)
            sp_name = get_user_name(o.assigned_sp_id)

            # Check Score
            latest_score = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == o.opp_id).order_by(desc(OppScoreVersion.version_no)).first()
            if latest_score:
                win_prob = latest_score.overall_score or 0
                version_no = latest_score.version_no

            if o.workflow_status:
                status = o.workflow_status
                if status == 'OPEN': status = None
            elif latest_score:
                if latest_score.status == 'SUBMITTED': status = "SUBMITTED_FOR_REVIEW"
                elif latest_score.status == 'DRAFT': status = "UNDER_ASSESSMENT"
                else: status = latest_score.status
            else:
                status = "NEW"

            results.append({
                "id": o.opp_id,
                "row_id": o.opp_id, # Same as id for standard rows
                "remote_id": o.opp_number or "N/A",
                "name": o.opp_name,
                "customer": o.customer_name,
                "practice": practice_name,
                "deal_value": o.deal_value or 0.0,
                "currency": o.currency or "USD",
                "workflow_status": status,
                "sales_stage": o.stage or "Prospecting",
                "geo": o.geo or "Global",
                "close_date": c_date_str,
                "sales_owner": sales_owner_name,
                "assigned_practice_head": ph_name, 
                "assigned_sales_head": sh_name,
                "assigned_sa": sa_name,
                "assigned_sp": sp_name,
                "win_probability": win_prob,
                "version_no": version_no,
                "gh_approval_status": o.gh_approval_status or 'PENDING',
                "ph_approval_status": o.ph_approval_status or 'PENDING',
                "sh_approval_status": o.sh_approval_status or 'PENDING',
                "assigned_practice_head_id": o.assigned_practice_head_id,
                "assigned_sales_head_id": o.assigned_sales_head_id,
                "combined_submission_ready": o.combined_submission_ready or False
            })

    return {
        "items": results, 
        "total_count": total_count,
        "total_value": pipeline_value,
        "avg_win_prob": 0,
        "counts": tab_counts
    }


class StartAssessmentInput(BaseModel):
    sa_name: Optional[str] = None

@router.post("/{opp_id}/start-assessment")
def start_assessment(opp_id: str, data: StartAssessmentInput, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    
    # Only change status if it's currently ASSIGNED_TO_SA or NEW
    opp.workflow_status = "UNDER_ASSESSMENT"
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to start assessment: {e}")
        
    return {"status": "success", "message": "Assessment started"}

# --- New Workflow Endpoints ---

class AssignRequest(BaseModel):
    role: str # PH, SH, SA, SP
    user_id: str
    assigned_by: str

@router.post("/{opp_id}/assign")
def assign_role(opp_id: str, req: AssignRequest, db: Session = Depends(get_db)):
    """
    Assign a role to an opportunity with proper state transitions.
    
    State Transitions:
    - NEW → HEADS_ASSIGNED (when both PH and SH assigned)
    - HEADS_ASSIGNED → EXECUTORS_ASSIGNED (when both SA and SP assigned)
    - EXECUTORS_ASSIGNED → IN_ASSESSMENT (when SA or SP starts assessment)
    """
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: 
        raise HTTPException(404, "Opportunity not found")
    
    target_user = db.query(AppUser).filter(AppUser.user_id == req.user_id).first()
    if not target_user: 
        raise HTTPException(404, "Target user not found")
    
    # Store current state for logging
    old_status = opp.workflow_status
    
    # Assign based on role
    # Assign based on role
    if req.role == 'PH':
        opp.assigned_practice_head_id = req.user_id
        if opp.workflow_status in ['NEW', 'OPEN', None, '']:
            if opp.assigned_sales_head_id:
                opp.workflow_status = 'HEADS_ASSIGNED'
            else:
                opp.workflow_status = 'PH_ASSIGNED'
            
    elif req.role == 'SH':
        opp.assigned_sales_head_id = req.user_id
        if opp.workflow_status in ['NEW', 'OPEN', None, '', 'PH_ASSIGNED']:
            if opp.assigned_practice_head_id:
                opp.workflow_status = 'HEADS_ASSIGNED'
            else:
                opp.workflow_status = 'SH_ASSIGNED'
            
    elif req.role == 'SA':
        opp.assigned_sa_id = req.user_id
        # If PH assigns SA, we can move forward even if SH hasn't assigned SP yet?
        # User says: "assigned individually... but same version".
        # Let's keep status as indicate progress.
        if opp.workflow_status in ['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED']:
             if opp.assigned_sp_id:
                 opp.workflow_status = 'EXECUTORS_ASSIGNED'
             else:
                 # Partial assignment
                 pass 
            
    elif req.role == 'SP':
        opp.assigned_sp_id = req.user_id
        if opp.workflow_status in ['HEADS_ASSIGNED', 'PH_ASSIGNED', 'SH_ASSIGNED']:
             if opp.assigned_sa_id:
                 opp.workflow_status = 'EXECUTORS_ASSIGNED'
             else:
                 # Partial
                 pass
    else:
        raise HTTPException(400, f"Invalid role: {req.role}")
    
    db.commit()
    db.refresh(opp)
    
    print(f"✅ Assignment: {req.role} → {target_user.display_name} | State: {old_status} → {opp.workflow_status}")
    
    return {
        "status": "success", 
        "message": f"Assigned {req.role} to {target_user.display_name}", 
        "workflow_status": opp.workflow_status,
        "previous_status": old_status
    }

class ApprovalRequest(BaseModel):
    role: str # GH, PH, SH
    decision: str # APPROVED, REJECTED
    comment: Optional[str] = None
    user_id: str

@router.post("/{opp_id}/approve")
def process_approval(opp_id: str, req: ApprovalRequest, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Opportunity not found")
    
    # Normalize decision
    decision = req.decision.upper()
    if decision == 'APPROVE': decision = 'APPROVED'
    if decision == 'REJECT': decision = 'REJECTED'
    
    # Update individual status
    if req.role == 'GH':
        opp.gh_approval_status = decision
    elif req.role == 'PH':
        opp.ph_approval_status = decision
    elif req.role == 'SH':
        opp.sh_approval_status = decision
    
    # Use normalized decision for subsequent logic
    logic_decision = decision
        
    # Get latest score to determine logic path
    latest_ver = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    current_score = latest_ver.overall_score if latest_ver and latest_ver.overall_score else 0
    
    # Normalized score (0-100) to 0-5 scale
    score_5 = (current_score / 100.0) * 5.0
    
    is_fast_track = (3.5 <= score_5 < 4.0)

    # 1. REJECTION Logic (Any rejection kills it)
    if logic_decision == 'REJECTED':
        opp.workflow_status = 'REJECTED'
        if latest_ver: latest_ver.status = 'REJECTED'
            
    # 2. APPROVAL Logic
    else:
        if is_fast_track:
            # Special Rule: Direct to GH. If GH approves, we consider it done.
            # "Overview assessment score between 3.5 to 4 need to go directly to Geo-Head... notified to PH or SH"
            if opp.gh_approval_status == 'APPROVED':
                opp.workflow_status = 'APPROVED'
                if latest_ver: latest_ver.status = 'APPROVED'
                # Optionally set PH/SH to 'NOTIFIED' if pending?
                if opp.ph_approval_status == 'PENDING': opp.ph_approval_status = 'NOTIFIED'
                if opp.sh_approval_status == 'PENDING': opp.sh_approval_status = 'NOTIFIED'
            else:
                # If GH hasn't approved yet (rejection handled above), wait for GH.
                # PH/SH approval status doesn't matter much here?
                opp.workflow_status = 'PENDING_GH_APPROVAL'
        else:
            # Standard Rule: Combined approval
            # Assuming all 3 must approve for now based on "Combined version... need to go to PH, GH, SH"
            if (opp.gh_approval_status == 'APPROVED' and 
                opp.ph_approval_status == 'APPROVED' and 
                opp.sh_approval_status == 'APPROVED'):
                opp.workflow_status = 'APPROVED'
                if latest_ver: latest_ver.status = 'APPROVED'
            else:
                 opp.workflow_status = 'PENDING_FINAL_APPROVAL'

    db.commit()
    return {
        "status": "success", 
        "gh_status": opp.gh_approval_status,
        "ph_status": opp.ph_approval_status,
        "sh_status": opp.sh_approval_status,
        "workflow_status": opp.workflow_status
    }
