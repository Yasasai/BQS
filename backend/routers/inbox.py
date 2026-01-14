
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.database import get_db, Opportunity, OpportunityAssignment, OppScoreVersion

router = APIRouter(prefix="/api/inbox", tags=["inbox"])

class InboxItem(BaseModel):
    opp_id: str
    opp_number: Optional[str]
    opp_name: str
    customer_name: str
    deal_value: float = 0
    crm_last_updated_at: datetime
    latest_score_status: str = "NOT_STARTED"

@router.get("/unassigned", response_model=List[InboxItem])
def get_unassigned_opportunities(db: Session = Depends(get_db)):
    assigned_subquery = db.query(OpportunityAssignment.opp_id).filter(OpportunityAssignment.status == "ACTIVE")
    opps = db.query(Opportunity).filter(Opportunity.is_active == True, ~Opportunity.opp_id.in_(assigned_subquery)).limit(100).all()
    return [
        {
            "opp_id": o.opp_id,
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
    assignments = db.query(OpportunityAssignment).filter(OpportunityAssignment.assigned_to_user_id == user_id, OpportunityAssignment.status == "ACTIVE").all()
    results = []
    for a in assignments:
        o = a.opportunity
        if not o: continue
        latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == o.opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        status = latest.status if latest else "NOT_STARTED"
        results.append({
            "opp_id": o.opp_id,
            "opp_number": o.opp_number,
            "opp_name": o.opp_name,
            "customer_name": o.customer_name,
            "deal_value": o.deal_value or 0,
            "crm_last_updated_at": o.crm_last_updated_at,
            "latest_score_status": status
        })
    return results

@router.post("/assign")
def assign_opportunity(opp_id: str, assigned_to_user_id: str, assigned_by_user_id: str, db: Session = Depends(get_db)):
    existing = db.query(OpportunityAssignment).filter(OpportunityAssignment.opp_id == opp_id, OpportunityAssignment.status == "ACTIVE").first()
    if existing: existing.status = "REVOKED"
    
    new_assign = OpportunityAssignment(opp_id=opp_id, assigned_to_user_id=assigned_to_user_id, assigned_by_user_id=assigned_by_user_id, status="ACTIVE")
    db.add(new_assign)
    db.commit()
    return {"status": "success"}

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
