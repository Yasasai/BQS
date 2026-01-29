
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.models import OppScoreVersion, OppScoreSectionValue, OppScoreSection

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
        
    return {
        "status": current_status,
        "overall_score": latest.overall_score if has_ratings else 0,
        "confidence_level": latest.confidence_level,
        "recommendation": latest.recommendation,
        "summary_comment": latest.summary_comment,
        "attachment_name": latest.attachment_name,
        "sections": sections
    }

@router.post("/{opp_id}/draft")
def save_draft(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    draft = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id, OppScoreVersion.status == "DRAFT").first()
    if not draft:
        last = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        ver = (last.version_no + 1) if last else 1
        draft = OppScoreVersion(opp_id=opp_id, version_no=ver, status="DRAFT", created_by_user_id=data.user_id)
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
    
    # 2. Get the draft we just saved/updated
    from sqlalchemy.orm import joinedload
    draft = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status == "DRAFT"
    ).first()
    
    if not draft:
        raise HTTPException(400, "Draft not found immediately after saving. Please try again.")
    
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
    db.commit()
    return {"status": "success", "message": "Assessment re-opened as draft."}

@router.get("/{opp_id}/history")
def get_scoring_history(opp_id: str, db: Session = Depends(get_db)):
    history = db.query(OppScoreVersion).filter(
        OppScoreVersion.opp_id == opp_id, 
        OppScoreVersion.status == "SUBMITTED"
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

