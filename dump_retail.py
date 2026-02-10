
import os
import sys
import json

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OppScoreVersion, OppScoreSectionValue

def dump_retail():
    db = SessionLocal()
    data = {"found": False}
    try:
        opp = db.query(Opportunity).filter(Opportunity.opp_name.like('%RetailCo%')).first()
        if opp:
            data = {
                "found": True,
                "opp_id": opp.opp_id,
                "workflow_status": opp.workflow_status,
                "versions": []
            }
            vers = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp.opp_id).all()
            for v in vers:
                vals = db.query(OppScoreSectionValue).filter(OppScoreSectionValue.score_version_id == v.score_version_id).all()
                data["versions"].append({
                    "version_no": v.version_no,
                    "status": v.status,
                    "user": v.created_by_user_id,
                    "score": v.overall_score,
                    "sections": [{"code": val.section_code, "score": val.score} for val in vals]
                })
    finally:
        db.close()
    
    with open('retail_dump.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    dump_retail()
