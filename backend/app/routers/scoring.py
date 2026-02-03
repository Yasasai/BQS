
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.models import OppScoreVersion, OppScoreSectionValue, OppScoreSection, Opportunity

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
def get_latest_score(opp_id: str, db: Session = Depends(get_db)):
    latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
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

    return {
        "status": current_status,
        "version_no": latest.version_no,
        "overall_score": latest.overall_score if has_ratings else 0,
        "confidence_level": latest.confidence_level,
        "recommendation": latest.recommendation,
        "summary_comment": latest.summary_comment,
        "attachment_name": latest.attachment_name,
        "sections": sections,
        "prev_assessment": prev_assessment
    }

@router.post("/{opp_id}/draft")
def save_draft(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    # 1. Find the latest version for this opportunity
    last = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    
    # 2. Determine if we can reuse the latest version (if it's not finalized)
    # Finalized statuses are SUBMITTED, APPROVED, REJECTED. 
    # Active/Draft-like statuses are DRAFT, ASSIGNED_TO_SA, UNDER_ASSESSMENT.
    active_statuses = ["DRAFT", "ASSIGNED_TO_SA", "UNDER_ASSESSMENT"]
    if last and last.status in active_statuses:
        draft = last
    else:
        # Create a new version if none exists or latest is finalized
        ver_no = (last.version_no + 1) if last else 1
        draft = OppScoreVersion(
            opp_id=opp_id, 
            version_no=ver_no, 
            status="UNDER_ASSESSMENT", # Default to UNDER_ASSESSMENT upon saving
            created_by_user_id=data.user_id
        )
        db.add(draft)
        db.flush()
    
    draft.confidence_level = data.confidence_level
    draft.recommendation = data.recommendation
    draft.summary_comment = data.summary_comment
    draft.attachment_name = data.attachment_name # Save attachment filename
    
    valid_sections = {s.section_code for s in db.query(OppScoreSection).all()}
    
    saved_count = 0
    for s in data.sections:
        if s.section_code not in valid_sections:
            print(f"⚠️ Warning: Frontend sent section '{s.section_code}' which is NOT in the database. Valid codes: {valid_sections}")
            continue

        val = db.query(OppScoreSectionValue).filter(
            OppScoreSectionValue.score_version_id == draft.score_version_id, 
            OppScoreSectionValue.section_code == s.section_code
        ).first()
        
        if val:
            val.score = s.score
            val.notes = s.notes
            val.selected_reasons = s.selected_reasons 
        else:
            db.add(OppScoreSectionValue(
                score_version_id=draft.score_version_id, 
                section_code=s.section_code, 
                score=s.score, 
                notes=s.notes,
                selected_reasons=s.selected_reasons 
            ))
        saved_count += 1
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Database Error during save: {e}")
        
    if saved_count == 0:
        # Critical warning: no data actually saved
        print(f"❌ Critical: Zero sections saved for {opp_id}. Frontend sent: {[s.section_code for s in data.sections]}")
        
    return {"status": "success", "saved_count": saved_count}



@router.post("/{opp_id}/submit")
def submit_score(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    # 1. Save data as draft first (this commits)
    save_draft(opp_id, data, db) 
    
    # 2. Get the active version we just saved/updated
    from sqlalchemy.orm import joinedload
    active_statuses = ["DRAFT", "ASSIGNED_TO_SA", "UNDER_ASSESSMENT"]
    draft = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status.in_(active_statuses)
    ).order_by(desc(OppScoreVersion.version_no)).first()
    
    if not draft:
        raise HTTPException(400, "Active assessment not found immediately after saving. Please try again.")
    
    # 3. Calculate Score using relationship
    total_w, weighted_s = 0, 0
    # Use joinedload to ensure 'section' is available for weights
    vals = db.query(OppScoreSectionValue).options(joinedload(OppScoreSectionValue.section)).filter(
        OppScoreSectionValue.score_version_id == draft.score_version_id
    ).all()
    
    if not vals:
        raise HTTPException(400, "No section scores found. Cannot calculate final score.")

    for v in vals:
        if v.section:
            weighted_s += (v.score * v.section.weight)
            total_w += v.section.weight
        else:
            # Fallback if section definition is somehow missing
            weighted_s += (v.score * 1.0)
            total_w += 1.0
    
    max_s = total_w * 5
    draft.overall_score = int((weighted_s / max_s) * 100) if max_s > 0 else 0
    draft.status = "SUBMITTED"
    draft.submitted_at = datetime.utcnow()
    
    # Update Opportunity Workflow Status
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if opp:
        opp.workflow_status = "SUBMITTED_FOR_REVIEW"
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to commit submission: {e}")
        
    return {"status": "success", "overall_score": draft.overall_score}


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
    ).order_by(desc(OppScoreVersion.submitted_at)).all()
    
    results = []
    for h in history:
        results.append({
            "version": h.version_no,
            "score": h.overall_score,
            "recommendation": h.recommendation,
            "summary": h.summary_comment,
            "created_at": h.submitted_at,
            "created_by": h.created_by_user_id
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
