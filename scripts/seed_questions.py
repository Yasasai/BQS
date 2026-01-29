import sys
import os

# Ensure backend module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal
from backend.app.models import OppScoreSection

def seed_sections():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        sections = [
            {"section_code": "q1", "section_name": "Commercial", "display_order": 1, "weight": 1.0},
            {"section_code": "q2", "section_name": "Feasibility", "display_order": 2, "weight": 1.0},
            {"section_code": "q3", "section_name": "Strategic", "display_order": 3, "weight": 1.0},
            {"section_code": "q4", "section_name": "Relationship", "display_order": 4, "weight": 1.0},
        ]
        
        for s in sections:
            existing = db.query(OppScoreSection).filter(OppScoreSection.section_code == s["section_code"]).first()
            if not existing:
                print(f"Creating section: {s['section_name']}")
                new_s = OppScoreSection(**s)
                db.add(new_s)
            else:
                print(f"Section exists: {s['section_name']}")
                
        db.commit()
        print("Seeding complete.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sections()
