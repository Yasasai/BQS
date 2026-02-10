
import os
import sys

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, OppScoreVersion, OppScoreSectionValue

def check_retail_versions():
    db = SessionLocal()
    try:
        opp = db.query(Opportunity).filter(Opportunity.opp_name.like('%RetailCo%')).first()
        if not opp:
            print("RetailCo NOT FOUND")
            return

        print(f"Checking Opp: {opp.opp_id} | {opp.opp_name}")
        versions = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp.opp_id).all()
        print(f"Total Versions: {len(versions)}")
        
        for v in versions:
            print(f"--- Version {v.version_no} ---")
            print(f"Status: {v.status}")
            print(f"Created By: {v.created_by_user_id}")
            print(f"Score: {v.overall_score}")
            vals = db.query(OppScoreSectionValue).filter(OppScoreSectionValue.score_version_id == v.score_version_id).all()
            print(f"Section Values: {len(vals)}")
            for val in vals:
                print(f"  - {val.section_code}: {val.score}")

    finally:
        db.close()

if __name__ == "__main__":
    check_retail_versions()
