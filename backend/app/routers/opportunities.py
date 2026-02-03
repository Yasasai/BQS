from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
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
    tab: Optional[str] = None
):
    # Calculate skip
    skip = (page - 1) * limit

    # Build Query
    query = db.query(Opportunity).filter(Opportunity.is_active == True)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
             (Opportunity.opp_name.ilike(search_term)) | 
             (Opportunity.customer_name.ilike(search_term)) |
             (Opportunity.opp_number.ilike(search_term))
        )

    from sqlalchemy import or_

    # Consolidated Tab Filtering (User Requested Buckets)
    if tab == 'unassigned':
        # All items that need assignment (New/Open/NULL)
        query = query.filter(
            or_(
                Opportunity.workflow_status.in_(['NEW', 'OPEN', '']),
                Opportunity.workflow_status.is_(None)
            )
        )
    elif tab == 'assigned':
        # Work Pipeline - Items already assigned or being worked on
        query = query.filter(Opportunity.workflow_status.in_(['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT']))
    elif tab == 'review':
        # Review Pipeline - Items submitted by SAs
        query = query.filter(Opportunity.workflow_status.in_(['SUBMITTED_FOR_REVIEW', 'SUBMITTED']))
    elif tab == 'completed':
        # Completed - Approved and Rejected items
        query = query.filter(Opportunity.workflow_status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']))
    # Note: 'all' or no tab returns everything unfiltered.

    # Get Metrics Across Full Filtered Query (Before Pagination)
    from sqlalchemy import func
    total_count = query.count()
    
    metrics = db.query(
        func.sum(Opportunity.deal_value).label("total_val")
    ).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).first()
    
    pipeline_value = metrics.total_val if metrics and metrics.total_val else 0
    
    # Calculate counts for all tabs to show in sidebar/tabs
    from sqlalchemy import or_
    total_all = db.query(Opportunity).filter(Opportunity.is_active == True).count()
    count_unassigned = db.query(Opportunity).filter(
        Opportunity.is_active == True,
        or_(Opportunity.workflow_status.in_(['NEW', 'OPEN', '']), Opportunity.workflow_status.is_(None))
    ).count()
    count_assigned = db.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.workflow_status.in_(['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT'])
    ).count()
    count_review = db.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.workflow_status.in_(['SUBMITTED_FOR_REVIEW', 'SUBMITTED'])
    ).count()
    count_completed = db.query(OppScoreVersion).join(Opportunity).filter(
        Opportunity.is_active == True,
        OppScoreVersion.status.in_(['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST'])
    ).count()

    tab_counts = {
        "all": total_all,
        "unassigned": count_unassigned,
        "assigned": count_assigned,
        "review": count_review,
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
                "version_no": v.version_no
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

            # Check Assignment
            active_assign = db.query(OpportunityAssignment).filter(
                OpportunityAssignment.opp_id == o.opp_id,
                OpportunityAssignment.status == 'ACTIVE'
            ).first()
            
            assigned_sa_name = None
            if active_assign:
                sa_user = db.query(AppUser).filter(AppUser.user_id == active_assign.assigned_to_user_id).first()
                if sa_user: assigned_sa_name = sa_user.display_name
            
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
                "assigned_practice_head": "N/A", 
                "assigned_sa": assigned_sa_name,
                "win_probability": win_prob,
                "version_no": version_no
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
    # We want to keep UNDER_ASSESSMENT or SUBMITTED_FOR_REVIEW as is if they are already there
    # But for a new version, the SA might click "Restore Session" or "Run Assessment"
    # Actually, let's just mark it as UNDER_ASSESSMENT once they start.
    opp.workflow_status = "UNDER_ASSESSMENT"
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to start assessment: {e}")
        
    return {"status": "success", "message": "Assessment started"}
