
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import func
from backend.app.core.database import get_db
from backend.app.models import OppScoreVersion, OppScoreSectionValue, OppScoreSection, Opportunity, AppUser

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

class SectionInput(BaseModel):
    section_code: str
    score: float # Changed from int to float to support 0.5 increments
    notes: Optional[str] = ""
    selected_reasons: Optional[List[str]] = []

class ScoreInput(BaseModel):
    user_id: str
    sections: List[SectionInput]
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None
    summary_comment: Optional[str] = None
    attachment_name: Optional[str] = None

@router.get("/{opp_id}/latest")
def get_latest_score(
    opp_id: str, 
    user_id: Optional[str] = Query(None), 
    version: Optional[int] = Query(None),
    db: Session = Depends(get_db)
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
    
    # LOGIC FIX: If an assessment is marked "SUBMITTED" but has no section values, 
    # it's likely a stale or dummy record. Treat it as NOT_STARTED to allow the user to fill it.
    if latest.status == "SUBMITTED" and not latest.section_values:
        return {"status": "NOT_STARTED", "sections": []}

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
    
    # DYNAMIC STATUS CHECK:
    # If all scores are 0, it means no rating has been given yet.
    has_ratings = any(s["score"] > 0 for s in sections)
    current_status = latest.status
    if not has_ratings:
        current_status = "NOT_STARTED"
        
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

    # GLOBAL STATUS CHECK:
    # We need to know if SA/SP have submitted, regardless of which version we are looking at.
    opp_obj = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    
    global_sa_submitted = False
    global_sp_submitted = False
    
    if opp_obj:
        sa_id = opp_obj.assigned_sa_id
        sp_id = opp_obj.assigned_sp_id
        
        if sa_id:
            sa_ver = db.query(OppScoreVersion).filter(
                OppScoreVersion.opp_id == opp_id,
                OppScoreVersion.created_by_user_id == sa_id,
                OppScoreVersion.status.in_(["SUBMITTED", "APPROVED", "REJECTED"])
            ).first()
            if sa_ver: global_sa_submitted = True
            
        if sp_id:
            sp_ver = db.query(OppScoreVersion).filter(
                OppScoreVersion.opp_id == opp_id,
                OppScoreVersion.created_by_user_id == sp_id,
                OppScoreVersion.status.in_(["SUBMITTED", "APPROVED", "REJECTED"])
            ).first()
            if sp_ver: global_sp_submitted = True

    return {
        "status": current_status,
        "version_no": latest.version_no,
        "overall_score": latest.overall_score if has_ratings else 0,
        "confidence_level": latest.confidence_level,
        "recommendation": latest.recommendation,
        "summary_comment": latest.summary_comment,
        "attachment_name": latest.attachment_name,
        "sa_submitted": global_sa_submitted,
        "sp_submitted": global_sp_submitted,
        "sections": sections,
        "prev_assessment": prev_assessment
    }

@router.post("/{opp_id}/draft")
def save_draft(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    # Fetch opp to check workflow status later
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(404, "Opportunity not found")
    # 1. Find the latest version FOR THIS USER
    last = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id,
        OppScoreVersion.created_by_user_id == data.user_id
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    # 2. Reuse latest version if it's not fully finalized
    # Fully finalized = APPROVED, REJECTED
    # If I have a draft that is UNDER_ASSESSMENT vs SUBMITTED...
    
    # Find the global latest version number for this opportunity (across all users)
    global_max_ver = db.query(func.max(OppScoreVersion.version_no)).filter(OppScoreVersion.opp_id == opp_id).scalar() or 0
    target_ver_no = global_max_ver if global_max_ver > 0 else 1
    
    # Collaborative check: Is the current version finalized?
    # If ANY record for this version is APPROVED/REJECTED, it means the round is closed.
    current_ver_record = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id,
        OppScoreVersion.version_no == target_ver_no
    ).order_by(desc(OppScoreVersion.created_at)).first()

    if current_ver_record and current_ver_record.status in ['APPROVED', 'REJECTED']:
        target_ver_no += 1
        current_ver_record = None

    if current_ver_record:
        # REUSE shared version for collaboration
        draft = current_ver_record
        # If the current user is an SA or SP, and they are saving a draft,
        # ensure their submission flag is reset if the version was previously submitted
        # and the workflow status allows re-opening.
        if opp.assigned_sa_id == data.user_id:
            draft.sa_submitted = False
        if opp.assigned_sp_id == data.user_id:
            draft.sp_submitted = False

        if draft.status == 'SUBMITTED' and opp.workflow_status not in ['APPROVED', 'REJECTED']:
             # Re-open if somehow marked submitted but global flow hasn't progressed
             draft.status = 'UNDER_ASSESSMENT'
    else:
        # Create a new version for this round
        draft = OppScoreVersion(
            opp_id=opp_id, 
            version_no=target_ver_no, 
            status="UNDER_ASSESSMENT", 
            created_by_user_id=data.user_id
        )
        db.add(draft)
        db.flush() # Get score_version_id
        
    db.flush()
    
    draft.confidence_level = data.confidence_level
    draft.recommendation = data.recommendation
    draft.summary_comment = data.summary_comment
    draft.attachment_name = data.attachment_name
    
    valid_sections = {s.section_code: s.section_code for s in db.query(OppScoreSection).all()}
    # Support Mapping for frontend descriptive keys to backend codes
    section_map = {
        "strategic_fit": "STRAT",
        "win_probability": "WIN",
        "financial_value": "FIN",
        "competitive_position": "COMP",
        "delivery_feasibility": "FEAS",
        "customer_relationship": "CUST",
        "risk_exposure": "RISK",
        "compliance": "PROD",
        "legal_readiness": "LEGAL"
    }
    
    saved_count = 0
    for s in data.sections:
        code = section_map.get(s.section_code, s.section_code) # Map or use default
        if code not in valid_sections:
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
            
    db.commit()
    return {"status": "success", "saved_count": saved_count, "version_no": draft.version_no}

@router.post("/{opp_id}/submit")
def submit_score(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    # 0. Pre-fetch Data
    user = db.query(AppUser).filter(AppUser.user_id == data.user_id).first()
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not user or not opp: raise HTTPException(404, "Data mismatch")

    # 1. Save current changes
    save_draft(opp_id, data, db) 
    
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
    
    # 3. Determine Role and Update Flags
    is_sa = (opp.assigned_sa_id == user.user_id)
    is_sp = (opp.assigned_sp_id == user.user_id)
    
    # Update this specific version's flags (though mostly we care about the version status)
    if is_sa: draft.sa_submitted = True
    if is_sp: draft.sp_submitted = True
    
    # Calculate Weighted Score
    total_w, weighted_s = 0, 0
    from sqlalchemy.orm import joinedload
    vals = db.query(OppScoreSectionValue).options(joinedload(OppScoreSectionValue.section)).filter(
        OppScoreSectionValue.score_version_id == draft.score_version_id
    ).all()
    
    for v in vals:
        if v.section:
            weighted_s += (v.score * v.section.weight)
            total_w += v.section.weight
    
    max_s = total_w * 5
    draft.overall_score = int((weighted_s / max_s) * 100) if max_s > 0 else 0
    
    # Check Combined Completion
    sa_id = opp.assigned_sa_id
    sp_id = opp.assigned_sp_id
    
    # Logic: Done if (No one assigned) or (Assigned and flag is True)
    sa_done = (sa_id is None) or draft.sa_submitted
    sp_done = (sp_id is None) or draft.sp_submitted

    # Fast Track Logic (3.5 - 4.0)
    score_5 = (draft.overall_score / 100.0) * 5.0
    is_fast_track = (3.5 <= score_5 <= 4.0)

    if sa_done and sp_done:
        # FULL SUBMISSION - Only if there is at least one actual submission
        if draft.sa_submitted or draft.sp_submitted:
            draft.status = "SUBMITTED"
            draft.submitted_at = datetime.utcnow()
            
            if is_fast_track:
                opp.workflow_status = "PENDING_GH_APPROVAL"
                if opp.ph_approval_status == 'PENDING': opp.ph_approval_status = 'NOTIFIED'
                if opp.sh_approval_status == 'PENDING': opp.sh_approval_status = 'NOTIFIED'
            else:
                opp.workflow_status = "READY_FOR_REVIEW"
        else:
            # Nothing actually submitted yet
            draft.status = "UNDER_ASSESSMENT"
            opp.workflow_status = "UNDER_ASSESSMENT"
    else:
        # PARTIAL SUBMISSION - Keep in Assessment but update global flow
        draft.status = "UNDER_ASSESSMENT" # Still taking input from the other party
        
        if is_fast_track:
            # Even partial can trigger fast track if score is in range
            opp.workflow_status = "PENDING_GH_APPROVAL"
            if is_sa and opp.sh_approval_status == 'PENDING': opp.sh_approval_status = 'NOTIFIED' 
            if is_sp and opp.ph_approval_status == 'PENDING': opp.ph_approval_status = 'NOTIFIED'
        else:
            if draft.sa_submitted: opp.workflow_status = "SA_SUBMITTED"
            elif draft.sp_submitted: opp.workflow_status = "SP_SUBMITTED"
            else: opp.workflow_status = "UNDER_ASSESSMENT"
        
    db.commit()
    return {"status": "success", "overall_score": draft.overall_score, "workflow_status": opp.workflow_status}

@router.get("/{opp_id}/combined-review")
@router.get("/{opp_id}/combined-review")
def get_combined_score(opp_id: str, version_no: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Fetch both SA and SP assessments for a side-by-side review.
    """
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: raise HTTPException(404, "Opportunity not found")
    
    # Find targets
    sa_id = opp.assigned_sa_id
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
    sa_user = db.query(AppUser).filter(AppUser.user_id == sa_id).first() if sa_id else None
    sp_user = db.query(AppUser).filter(AppUser.user_id == sp_id).first() if sp_id else None

    return {
        "opp_id": opp_id,
        "ready_for_review": (ver.sa_submitted and ver.sp_submitted) if ver else False,
        "sa_assessment": unified if (ver and ver.sa_submitted) else None,
        "sp_assessment": unified if (ver and ver.sp_submitted) else None,
        "sa_info": {"id": sa_id, "name": sa_user.display_name if sa_user else "Not Assigned"},
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
def reopen_assessment(opp_id: str, db: Session = Depends(get_db)):
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
def get_scoring_history(opp_id: str, db: Session = Depends(get_db)):
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
def create_new_version(opp_id: str, db: Session = Depends(get_db)):
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
def approve_score(opp_id: str, db: Session = Depends(get_db)):
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
def reject_score(opp_id: str, data: RejectInput, db: Session = Depends(get_db)):
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
