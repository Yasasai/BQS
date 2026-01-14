
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from backend.database import get_db, OppScoreVersion, OppScoreSectionValue, OppScoreSection

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

class SectionInput(BaseModel):
    section_code: str
    score: int
    notes: Optional[str] = ""

class ScoreInput(BaseModel):
    user_id: str
    sections: List[SectionInput]
    confidence_level: Optional[str] = None
    recommendation: Optional[str] = None
    summary_comment: Optional[str] = None

@router.get("/{opp_id}/latest")
def get_latest_score(opp_id: str, db: Session = Depends(get_db)):
    latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    if not latest: return {"status": "NOT_STARTED", "sections": []}
    
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
            "score": val.score if val else 0,
            "notes": val.notes if val else ""
        })
        
    return {
        "status": latest.status,
        "overall_score": latest.overall_score,
        "confidence_level": latest.confidence_level,
        "recommendation": latest.recommendation,
        "summary_comment": latest.summary_comment,
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
    
    for s in data.sections:
        val = db.query(OppScoreSectionValue).filter(OppScoreSectionValue.score_version_id == draft.score_version_id, OppScoreSectionValue.section_code == s.section_code).first()
        if val:
            val.score = s.score
            val.notes = s.notes
        else:
            db.add(OppScoreSectionValue(score_version_id=draft.score_version_id, section_code=s.section_code, score=s.score, notes=s.notes))
            
    db.commit()
    return {"status": "success"}

@router.post("/{opp_id}/submit")
def submit_score(opp_id: str, data: ScoreInput, db: Session = Depends(get_db)):
    save_draft(opp_id, data, db) # Save first
    draft = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id, OppScoreVersion.status == "DRAFT").first()
    
    # Calculate Score
    total_w, weighted_s = 0, 0
    vals = db.query(OppScoreSectionValue, OppScoreSection).join(OppScoreSection, OppScoreSection.section_code == OppScoreSectionValue.section_code).filter(OppScoreSectionValue.score_version_id == draft.score_version_id).all()
    
    for v, d in vals:
        weighted_s += (v.score * d.weight)
        total_w += d.weight
    
    max_s = total_w * 5
    draft.overall_score = int((weighted_s / max_s) * 100) if max_s > 0 else 0
    draft.status = "SUBMITTED"
    draft.submitted_at = datetime.utcnow()
    db.commit()
    return {"status": "success"}
