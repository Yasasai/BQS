from sqlalchemy.orm import Session, joinedload
from backend.app.models import OppScoreSectionValue

def calculate_weighted_score(db: Session, score_version_id: int) -> int:
    """
    Calculates the weighted overall score for a specific assessment version.
    Formula: (sum(score * weight) / (sum(weight) * 5)) * 100
    Returns an integer percentage (0-100).
    """
    total_w, weighted_s = 0, 0
    vals = db.query(OppScoreSectionValue).options(joinedload(OppScoreSectionValue.section)).filter(
        OppScoreSectionValue.score_version_id == score_version_id
    ).all()
    
    for v in vals:
        if v.section:
            weighted_s += (v.score * v.section.weight)
            total_w += v.section.weight
    
    max_s = total_w * 5
    return int((weighted_s / max_s) * 100) if max_s > 0 else 0
