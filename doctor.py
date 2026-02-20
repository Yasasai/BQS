
import os
import sys
from sqlalchemy import create_engine, text
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity, AppUser, OppScoreSection

def doctor(opp_id):
    print(f"--- Diagnosing Opportunity: {opp_id} ---")
    db = SessionLocal()
    try:
        opp = db.query(Opportunity).filter_by(opp_id=opp_id).first()
        if opp:
            print(f"✅ Opportunity exists: {opp.opp_name}")
        else:
            print(f"❌ Opportunity MISSING: {opp_id}")
            
        users = db.query(AppUser).all()
        print(f"Users in DB: {[u.display_name for u in users]}")
        
        sections = db.query(OppScoreSection).all()
        print(f"Sections in DB: {[s.section_code for s in sections]}")
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        doctor(sys.argv[1])
    else:
        print("Usage: python doctor.py <opp_id>")
