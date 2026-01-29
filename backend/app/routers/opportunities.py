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
    workflow_status: str
    sales_stage: Optional[str]
    geo: Optional[str]
    close_date: Optional[str]
    sales_owner: Optional[str]
    assigned_practice_head: Optional[str]
    assigned_sa: Optional[str]
    win_probability: Optional[float] = 0

@router.get("/", response_model=List[OpportunityResponse])
def get_all_opportunities(db: Session = Depends(get_db)):
    # Fetch all active opportunities
    opps = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    
    results = []
    for o in opps:
        # Determine Status
        status = "NEW"
        
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
            
            if not has_ratings:
                status = "ASSIGNED_TO_SA" if active_assign else "NEW"
            elif latest_score.status == 'SUBMITTED':
                status = "SUBMITTED_FOR_REVIEW"
            elif latest_score.status == 'ACCEPTED':
                status = "COMPLETED"
            elif latest_score.status == 'REJECTED':
                status = "COMPLETED"
            else:
                status = "UNDER_ASSESSMENT"
        elif active_assign:
            status = "ASSIGNED_TO_SA"
            
        # Resolve Practice Name
        practice_name = "General"
        if o.primary_practice_id:
            prac = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
            if prac:
                practice_name = prac.practice_name
        
        # Resolve Sales Owner Name (Optional)
        sales_owner_name = "Unassigned"
        if o.sales_owner_user_id:
            u = db.query(AppUser).filter(AppUser.user_id == o.sales_owner_user_id).first()
            if u:
                sales_owner_name = u.display_name
                
        # Format Date
        c_date_str = ""
        if o.close_date:
            c_date_str = o.close_date.isoformat()
        else:
            c_date_str = datetime.now().isoformat()

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
            "assigned_practice_head": "N/A", # Placeholder
            "assigned_sa": assigned_sa_name,
            "win_probability": 0 # Placeholder
        })
        
    return results
