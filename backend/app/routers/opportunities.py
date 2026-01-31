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

@router.get("/", response_model=List[OpportunityResponse])
def get_all_opportunities(db: Session = Depends(get_db)):
    # Fetch all active opportunities
    print("🔍 Querying opportunities from database...")
    opps = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    print(f"📊 Found {len(opps)} opportunities in database")
    
    results = []
    for o in opps:
        # Determine Status
        status = "NEW"
        win_prob = 0
        version_no = None
        has_ratings = False
        practice_name = "General"  # Default
        sales_owner_name = "Unknown"  # Default
        c_date_str = o.close_date.strftime("%Y-%m-%d") if o.close_date else None

        # Resolve Practice
        if o.primary_practice_id:
            practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
            if practice:
                practice_name = practice.practice_name

        # Resolve Sales Owner
        if o.sales_owner_user_id:
            owner = db.query(AppUser).filter(AppUser.user_id == o.sales_owner_user_id).first()
            if owner:
                sales_owner_name = owner.display_name

        # Check Assignment
        active_assign = db.query(OpportunityAssignment).filter(
            OpportunityAssignment.opp_id == o.opp_id,
            OpportunityAssignment.status == 'ACTIVE'
        ).first()
        
        assigned_sa_name = None
        if active_assign:
            sa_user = db.query(AppUser).filter(AppUser.user_id == active_assign.assigned_to_user_id).first()
            if sa_user:
                assigned_sa_name = sa_user.display_name
        
        # Check Score
        latest_score = db.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == o.opp_id
        ).order_by(desc(OppScoreVersion.version_no)).first()
        
        if latest_score:
            # Check if any non-zero ratings exist
            has_ratings = latest_score.section_values and any(sv.score > 0 for sv in latest_score.section_values)
            
            # Map Win Probability if available
            if latest_score.overall_score:
                win_prob = latest_score.overall_score
            
            version_no = latest_score.version_no

        if o.workflow_status:
            status = o.workflow_status
            # Auto-normalize 'OPEN' to None (null) per user request
            if status == 'OPEN':
                status = None
        elif latest_score:
            # Fallback to score status if workflow_status is missing
            if latest_score.status == 'SUBMITTED':
                status = "SUBMITTED_FOR_REVIEW"
            elif latest_score.status == 'DRAFT':
                status = "UNDER_ASSESSMENT"
            else:
                status = latest_score.status
        else:
            # Default to NEW if no explicit status and no score
            # This ensures items with NULL status appear in "Unassigned" even if they have an assignment record
            status = "NEW"

        results.append({
            "id": o.opp_id,
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

    # Detailed Audit Log for Terminal
    unassigned_count = sum(1 for r in results if r['assigned_sa'] is None)
    print(f"✅ Returning {len(results)} opportunities. Unassigned Count: {unassigned_count}")
    if unassigned_count > 0:
        print("   🔍 Unassigned Sample IDs:")
        for r in results:
            if r['assigned_sa'] is None:
                print(f"      - {r['id']} (Status: {r['workflow_status']})")
    else:
        print("   ⚠️ WARNING: Sending 0 unassigned items!")

    return results

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
