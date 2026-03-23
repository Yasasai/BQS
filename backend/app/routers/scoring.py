from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.models import OppScoreVersion, OppScoreSectionValue, OppScoreSection, Opportunity, AppUser
from backend.app.services.opportunity_service import OpportunityService
from backend.app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/api/scoring", tags=["scoring"])
logger = logging.getLogger(__name__)

REASON_OPTIONS = {
    "STRAT": { # Strategic Fit
        "critical": ["Extreme Misalignment", "Competitor Stronghold", "Legal/Regulatory Barrier"],
        "low": ["Geography Mismatch", "Technology Stack Mismatch", "Low Priority Region"],
        "average": ["Standard Offering", "Opportunistic Bid", "Minor Customization Needed"],
        "high": ["Target Client Account", "Strong Portfolio Addition", "Key Growth Area"],
        "exceptional": ["Board-Level Strategic Priority", "Market Entry Milestone", "CEO-Led Initiative"]
    },
    "WIN": { # Win Probability
        "critical": ["Late Entry (Post-RFP)", "Known RFP Bias", "Blacklisted by Client"],
        "low": ["Strong Incumbent", "No Capture History", "No Executive Access"],
        "average": ["Competitive Field", "Standard RFP Process", "Average Win Rate"],
        "high": ["Preferred Solution", "Niche Capability Leader", "Captured Early"],
        "exceptional": ["Single Source / Wired", "Exclusive Proof of Concept", "Incumbent with 100% Satisfaction"]
    },
    "COMP": { # Competitive Position
        "critical": ["No Product Fit", "Worst-in-Class Feature Set", "Unproven Technology"],
        "low": ["Weak Positioning", "Generic Offering", "Low Brand Awareness"],
        "average": ["Top 3 Contender", "Equal Footing", "Standard Differentiators"],
        "high": ["Unique Value Prop", "Sole Source Potential", "Exclusive Partnership"],
        "exceptional": ["Unrivaled Tech Superiority", "Monopoly Position", "Patent Protected Solution"]
    },
    "FIN": { # Financial Value
        "critical": ["Negative Margin Deal", "Unfunded Project", "Unacceptable Terms"],
        "low": ["Low Margins", "High Cost of Sales", "Payment Terms Issue"],
        "average": ["Standard Margins", "Acceptable Budget", "Moderate CAPEX"],
        "high": ["High Margins", "Recurring Revenue Model", "Budget Approved/Funded"],
        "exceptional": ["Strategic Multi-Year Lock-in", "Massive TCV Upside", "Pre-Paid Contract"]
    },
    "FEAS": { # Delivery Feasibility
        "critical": ["Total Skill Mismatch", "Severe Talent Shortage", "Zero Infrastructure"],
        "low": ["Hiring Required", "Overbooked Experts", "Training Required"],
        "average": ["Partial Availability", "Subcontractors Needed", "Standard Lead Times"],
        "high": ["Team Bench Available", "Key Experts Ready", "Reusable Assets"],
        "exceptional": ["Fully Automated Delivery", "Global Team on Standby", "Plug-and-Play Implementation"]
    },
    "CUST": { # Customer Relationship
        "critical": ["Hostile Relationship", "Past Legal Dispute", "Direct Competitor Champion"],
        "low": ["No Previous Contact", "Cold Relationship", "Blocked by Gatekeeper"],
        "average": ["Transactional Contact", "New Stakeholders", "Neutral Reputation"],
        "high": ["Trusted Advisor Status", "Executive Sponsorship", "Coach in Account"],
        "exceptional": ["Partnership Alliance", "Shared Success Roadmap", "Co-Innovation Partner"]
    },
    "RISK": { # Risk Exposure
        "critical": ["High Probability Catastrophic Risk", "Sovereign Default Risk", "Criminal Liability"],
        "low": ["Undefined Scope", "Performance Penalties", "Complex Dependencies"],
        "average": ["Manageable Commercial Risk", "Standard Penalties", "Stable Environment"],
        "high": ["Well Defined Scope", "Stable Growth Area", "Low Dependencies"],
        "exceptional": ["Risk Transfer to Partner", "Zero Liability Clauses", "Fully Guaranteed Success"]
    },
    "PROD": { # Product / Service Compliance
        "critical": ["Major Regulatory Breach", "Security Red-Flag", "Zero Sovereignty"],
        "low": ["Non-Compliance", "Certifications Missing", "Workaround Required"],
        "average": ["Minor Deviation", "Waiver Potential", "Standard Data Handling"],
        "high": ["Fully Compliant", "Exceeds Standards", "Security Certified"],
        "exceptional": ["Gold Standard Industry Benchmark", "Pre-Approved by Regulator", "All Certs Active"]
    },
    "LEGAL": { # Legal & Commercial Readiness
        "critical": ["Unlimited Liability", "No Termination Clause", "Loss of IP Control"],
        "low": ["Unfavorable Terms", "Bonding Issues", "Non-Standard SLA"],
        "average": ["Standard Terms", "Negotiable Clauses", "Acceptable Risk"],
        "high": ["Favorable Terms", "Pre-negotiated MSA", "IP Retained"],
        "exceptional": ["Standard Non-Negotiated MSA", "Zero IP Conflict", "Favorable Gov-Contract"]
    }
}

@router.get("/config")
def get_scoring_config(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    """
    Returns the active scoring sections and weights from the database.
    (Task 2: Eliminate Split-Brain Configuration)
    """
    sections = db.query(OppScoreSection).order_by(OppScoreSection.display_order).all()
    return [
        {
            "section_code": s.section_code,
            "section_name": s.section_name,
            "weight": s.weight,
            "display_order": s.display_order,
            "reasons": REASON_OPTIONS.get(s.section_code, {})
        }
        for s in sections
    ]

class SectionInput(BaseModel):
    section_code: str
    score: float # Changed from int to float to support 0.5 increments
    notes: Optional[str] = ""
    selected_reasons: Optional[List[str]] = []

class TeamInput(BaseModel):
    practice_head_ids: Optional[List[str]] = None
    sa_ids: Optional[List[str]] = None
    sales_head: Optional[str] = None
    sp: Optional[str] = None
    legal: Optional[str] = None
    finance: Optional[str] = None

class ScoreInput(BaseModel):
    user_id: Optional[str] = None # Optional now, will use current_user if missing
    sections: List[SectionInput]
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None
    summary_comment: Optional[str] = None
    attachment_name: Optional[str] = None
    financials: Optional[dict] = None # {deal_value: float, margin_percentage: float}
    team: Optional[TeamInput] = None

@router.get("/{opp_id}/latest")
def get_latest_score(
    opp_id: str, 
    user_id: Optional[str] = Query(None), 
    version: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    """
    Returns the latest assessment version for this user/opportunity.
    If 'version' is provided, returns that specific version.
    """
    query = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id)
    latest = None
    
    if version:
        latest = query.filter(OppScoreVersion.version_no == version).order_by(desc(OppScoreVersion.created_at)).first()
    else:
        # Prioritize the overall latest version, regardless of who started it
        latest = query.order_by(desc(OppScoreVersion.version_no), desc(OppScoreVersion.created_at)).first()

    if not latest: return {"status": "NOT_STARTED", "sections": []}
    
    # Remove legacy logic fix that resets status to NOT_STARTED

    # Simple serialization
    sections = []
    value_map = {v.section_code: v for v in latest.section_values}
    # Get definitions to ensure structure
    defs = db.query(OppScoreSection).order_by(OppScoreSection.display_order).all()
    
    for d in defs:
        val = value_map.get(d.section_code)
        sections.append({
            "section_code": d.section_code,
            "section_name": d.section_name,
            "weight": d.weight,
            "score": val.score if val else 0,
            "notes": val.notes if val else "",
            "selected_reasons": val.selected_reasons if val else []
        })
    
    # Use the actual status from the database without forced overrides
    current_status = latest.status
    # has_ratings check removed to prevent 'ghost save' reset
        
    # Get Previous Version for Summary Block
    prev_assessment = None
    prev = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.version_no < latest.version_no
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    if prev:
        prev_assessment = {
            "version_no": prev.version_no,
            "status": prev.status,
            "overall_score": prev.overall_score or 0,
            "recommendation": prev.recommendation,
            "summary_comment": prev.summary_comment,
            "created_at": prev.submitted_at or prev.created_at,
            "created_by": prev.created_by_user_id
        }

    # GLOBAL STATUS CHECK removed as Bid Manager now exclusively owns the scoring process.
    # We only need the opportunity object for locking metadata.
    opp_obj = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    
    return {
        "status": current_status,
        "version_no": latest.version_no,
        "overall_score": latest.overall_score or 0,
        "confidence_level": latest.confidence_level,
        "recommendation": latest.recommendation,
        "summary_comment": latest.summary_comment,
        "attachment_name": latest.attachment_name,
        "sections": sections,
        "prev_assessment": prev_assessment,
        "locked_by": opp_obj.locked_by if opp_obj else None,
        "locked_at": opp_obj.locked_at if opp_obj else None
    }

@router.post("/{opp_id}/draft")
def save_draft(opp_id: str, data: ScoreInput, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can modify scores.")
    
    user_id = data.user_id or current_user.user_id
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(404, "Opportunity not found")

    # Closed-state guard — no edits permitted on CLOSED opportunities
    if opp.workflow_status == 'CLOSED':
        raise HTTPException(status_code=409, detail="Assessment cannot be modified on a CLOSED opportunity.")

    # Task 1: Concurrency Control (Locking)
    # Check if locked by another user
    if opp.locked_by and opp.locked_by != user_id:
        # Check if lock is fresh (last 15 mins)
        now = datetime.now(timezone.utc)
        lock_at = opp.locked_at
        if lock_at.tzinfo is None:
            lock_at = lock_at.replace(tzinfo=timezone.utc)
        
        lock_duration = (now - lock_at).total_seconds()
        if lock_duration < 900: # 15 minutes
            locked_user = db.query(AppUser).filter(AppUser.user_id == opp.locked_by).first()
            user_name = locked_user.display_name if locked_user else "Another user"
            raise HTTPException(409, f"This assessment is currently being edited by {user_name}")
    
    # Update lock
    opp.locked_by = user_id
    opp.locked_at = datetime.now(timezone.utc)
    db.flush()

    # 1. Simplified version management: Always use the latest version for this opportunity
    # regardless of who created it, unless it's finalized (APPROVED/REJECTED)
    draft = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    
    if draft and draft.status in ['APPROVED', 'REJECTED']:
        # Create a new version if the current one is finalized
        new_ver_no = draft.version_no + 1
        draft = OppScoreVersion(
            opp_id=opp_id,
            version_no=new_ver_no,
            status="UNDER_ASSESSMENT",
            created_by_user_id=user_id
        )
        db.add(draft)
        db.flush()
    elif not draft:
        # Initial version
        draft = OppScoreVersion(
            opp_id=opp_id,
            version_no=1,
            status="UNDER_ASSESSMENT",
            created_by_user_id=user_id
        )
        db.add(draft)
        db.flush()
    else:
        # Re-use current draft
        if draft.status == "SUBMITTED":
            draft.status = "UNDER_ASSESSMENT" # Re-open for the BM to edit
    
    db.flush()
    
    draft.confidence_level = data.confidence_level
    draft.recommendation = data.recommendation
    draft.summary_comment = data.summary_comment
    draft.attachment_name = data.attachment_name
    
    valid_sections = {s.section_code: s.section_code for s in db.query(OppScoreSection).all()}
    saved_count = 0
    for s in data.sections:
        code = s.section_code 
        if code not in valid_sections:
            logger.warning(f"Skipping unknown section code: {code}")
            continue

        val = db.query(OppScoreSectionValue).filter(
            OppScoreSectionValue.score_version_id == draft.score_version_id, 
            OppScoreSectionValue.section_code == code
        ).first()
        
        if val:
            val.score = s.score
            val.notes = s.notes
            val.selected_reasons = s.selected_reasons 
        else:
            db.add(OppScoreSectionValue(
                score_version_id=draft.score_version_id, 
                section_code=code, 
                score=s.score, 
                notes=s.notes,
                selected_reasons=s.selected_reasons 
            ))
        saved_count += 1
            
    # Task 3: Handle Financials and Team updates
    if data.financials:
        if 'deal_value' in data.financials: opp.deal_value = data.financials['deal_value']
        if 'margin_percentage' in data.financials: opp.margin_percentage = data.financials['margin_percentage']
        if 'pat_margin' in data.financials: opp.pat_margin = data.financials['pat_margin']
    
    if data.team:
        if data.team.practice_head_ids: opp.assigned_practice_head_ids = data.team.practice_head_ids
        if data.team.sa_ids: opp.assigned_sa_ids = data.team.sa_ids
        if data.team.sales_head: opp.assigned_sales_head_id = data.team.sales_head
        if data.team.sp: opp.assigned_sp_id = data.team.sp
        if data.team.finance: opp.assigned_finance_id = data.team.finance
        if data.team.legal: opp.assigned_legal_id = data.team.legal
        
    db.commit()
    return {"status": "success", "saved_count": saved_count, "version_no": draft.version_no}

@router.post("/{opp_id}/submit")
def submit_score(opp_id: str, data: ScoreInput, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can modify scores.")
        
    try:
        user_id = data.user_id or current_user.user_id
        # 0. Pre-fetch Data
        user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
        opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
        if not user or not opp: raise HTTPException(404, "Data mismatch")

        # 1. Save current changes
        save_draft(opp_id, data, db, current_user=current_user) 
        
        # 2. Get active shared draft
        draft = db.query(OppScoreVersion).filter(
            OppScoreVersion.opp_id == opp_id
        ).order_by(desc(OppScoreVersion.version_no)).first()
        
        if not draft:
            raise HTTPException(400, "No active draft to submit")
        
        if draft.status in ["APPROVED", "REJECTED"]:
            raise HTTPException(400, "Cannot re-submit a finalized assessment (Approved/Rejected).")

        # Workflow status check to prevent submission after final decision
        if opp.workflow_status in ['APPROVED', 'REJECTED']:
             raise HTTPException(400, "Opportunity is already finalized.")
        
        # 3. Finalize and Submit
        draft.status = "SUBMITTED"
        draft.submitted_at = datetime.now(timezone.utc)
        draft.overall_score = OpportunityService.calculate_overall_score(db, draft.score_version_id)

        # GO / NO-GO determination from configurable threshold (spec §11.3)
        draft.recommendation = OpportunityService.evaluate_go_no_go(db, draft.overall_score)

        # Update Opportunity Status
        opp.workflow_status = "READY_FOR_REVIEW"

        # Financial Threshold Tripwire
        OpportunityService.evaluate_compliance_routing(opp_id, db)
            
        db.commit()
        return {"status": "success", "overall_score": draft.overall_score, "workflow_status": opp.workflow_status}
    except Exception as e:
        logger.error(f"Scoring Submit API Crashed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{opp_id}/combined-review")
def get_combined_score(opp_id: str, version_no: Optional[int] = Query(None), db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    """
    Fetch both SA and SP assessments for a side-by-side review.
    """
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Opportunity not found")
    
    # Find targets
    sa_ids = opp.assigned_sa_ids or []
    sp_id = opp.assigned_sp_id
    
    # Fetch only the single shared version record
    q = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id)
    if version_no:
        ver = q.filter(OppScoreVersion.version_no == version_no).first()
    else:
        ver = q.order_by(desc(OppScoreVersion.version_no)).first()

    # Helper to serialize
    def serialize_ver(v):
        if not v: return None
        sections = []
        for val in v.section_values:
            sections.append({
                "section_code": val.section_code,
                "score": val.score,
                "notes": val.notes
            })
        
        creator = db.query(AppUser).filter(AppUser.user_id == v.created_by_user_id).first()
        
        return {
            "version": v.version_no,
            "overall_score": v.overall_score,
            "score": v.overall_score,
            "status": v.status,
            "sections": sections,
            "confidence": v.confidence_level,
            "recommendation": v.recommendation,
            "created_by": v.created_by_user_id,
            "user_name": creator.display_name if creator else "Unknown",
            "sa_submitted": v.sa_submitted,
            "sp_submitted": v.sp_submitted,
            "submitted_at": v.submitted_at
        }

    unified = serialize_ver(ver)

    # Resolve SA and SP names even if they haven't submitted
    sa_user = db.query(AppUser).filter(AppUser.user_id == sa_ids[0]).first() if sa_ids else None
    sp_user = db.query(AppUser).filter(AppUser.user_id == sp_id).first() if sp_id else None

    return {
        "opp_id": opp_id,
        "ready_for_review": (ver.sa_submitted and ver.sp_submitted) if ver else False,
        "sa_assessment": unified if (ver and ver.sa_submitted) else None,
        "sp_assessment": unified if (ver and ver.sp_submitted) else None,
        "sa_info": {"id": sa_ids[0] if sa_ids else None, "name": sa_user.display_name if sa_user else "Not Assigned"},
        "sp_info": {"id": sp_id, "name": sp_user.display_name if sp_user else "Not Assigned"},
        "sa_submitted": ver.sa_submitted if ver else False,
        "sp_submitted": ver.sp_submitted if ver else False,
        "approvals": {
            "gh": opp.gh_approval_status,
            "ph": opp.ph_approval_status,
            "sh": opp.sh_approval_status
        }
    }


@router.post("/{opp_id}/reopen")
def reopen_assessment(opp_id: str, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can modify scores.")
        
    latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id, OppScoreVersion.status == "SUBMITTED").order_by(desc(OppScoreVersion.version_no)).first()
    if not latest:
        raise HTTPException(404, "No submitted assessment found to re-open.")
    
    latest.status = "DRAFT"
    latest.submitted_at = None
    
    # Update Opportunity Workflow Status
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if opp:
        opp.workflow_status = "UNDER_ASSESSMENT"

    db.commit()
    return {"status": "success", "message": "Assessment re-opened as draft."}

@router.get("/{opp_id}/history")
def get_scoring_history(opp_id: str, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    history = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status.in_(["SUBMITTED", "APPROVED", "REJECTED"])
    ).order_by(desc(OppScoreVersion.version_no), desc(OppScoreVersion.submitted_at)).all()
    
    results = []
    for h in history:
        creator = db.query(AppUser).filter(AppUser.user_id == h.created_by_user_id).first()
        results.append({
            "version": h.version_no,
            "status": h.status,
            "score": h.overall_score,
            "recommendation": h.recommendation,
            "summary": h.summary_comment,
            "attachment_name": h.attachment_name,
            "created_at": h.submitted_at or h.created_at,
            "created_by": creator.display_name if creator else h.created_by_user_id
        })
    return results

@router.post("/{opp_id}/new-version")
def create_new_version(opp_id: str, db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
    if 'BM' not in user_role_codes:
        raise HTTPException(status_code=403, detail="Only Bid Managers can modify scores.")
        
    # 1. Get the latest version (regardless of status)
    last = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    
    if not last:
        raise HTTPException(400, "No existing assessment version found to clone.")

    # 2. Create new version
    new_ver_no = last.version_no + 1
    new_version = OppScoreVersion(
        opp_id=opp_id,
        version_no=new_ver_no,
        status="DRAFT",
        created_by_user_id=last.created_by_user_id, 
        confidence_level=last.confidence_level,
        recommendation=last.recommendation,
        summary_comment=last.summary_comment,
        attachment_name=last.attachment_name
    )
    db.add(new_version)
    db.flush()

    # 3. Clone section values
    from backend.app.models import OppScoreSectionValue
    old_values = db.query(OppScoreSectionValue).filter(OppScoreSectionValue.score_version_id == last.score_version_id).all()
    
    for val in old_values:
        db.add(OppScoreSectionValue(
            score_version_id=new_version.score_version_id,
            section_code=val.section_code,
            score=val.score,
            notes=val.notes,
            selected_reasons=val.selected_reasons
        ))
    
    # 4. Update Opportunity Workflow Status
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if opp:
        opp.workflow_status = "UNDER_ASSESSMENT"

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to create new version: {e}")

    return {"status": "success", "new_version": new_ver_no}

@router.post("/{opp_id}/review/approve")
def approve_score(opp_id: str, db: Session = Depends(get_db), current_user: AppUser = Depends(require_role(["GH", "PH", "SH"]))):
    # 1. Update Score Version
    latest = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status == "SUBMITTED"
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    if latest:
        latest.status = "APPROVED"
    
    # 2. Update Opportunity Workflow
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
        
    opp.workflow_status = "APPROVED"
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Approve failed: {e}")
        
    return {"status": "success", "message": "Opportunity approved"}

class RejectInput(BaseModel):
    reason: str

@router.post("/{opp_id}/review/reject")
def reject_score(opp_id: str, data: RejectInput, db: Session = Depends(get_db), current_user: AppUser = Depends(require_role(["GH", "PH", "SH"]))):
    # 1. Update Score Version
    latest = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status == "SUBMITTED"
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    if latest:
        latest.status = "REJECTED"
        # Append reason to summary for history
        current_summary = latest.summary_comment or ""
        latest.summary_comment = f"[REJECTED]: {data.reason} | {current_summary}"
    
    # 2. Update Opportunity Workflow
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
        
    opp.workflow_status = "REJECTED"
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Reject failed: {e}")
        
    return {"status": "success", "message": "Opportunity rejected"}
