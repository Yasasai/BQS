
from sqlalchemy import create_engine, text
from backend.app.core.database import SessionLocal, init_db
from backend.app.models import OppScoreSection, AppUser
import uuid

def repair():
    print("Repairing sections...")
    init_db()
    db = SessionLocal()
    try:
        # Ensure all 8 sections exist
        expected = [
            ("STRAT", "Strategic Fit", 1, 0.15),
            ("WIN", "Win Probability", 2, 0.15),
            ("FIN", "Financial Value", 3, 0.15),
            ("COMP", "Competitive Position", 4, 0.10),
            ("FEAS", "Delivery Feasibility", 5, 0.10),
            ("CUST", "Customer Relationship", 6, 0.10),
            ("RISK", "Risk Exposure", 7, 0.10),
            ("PROD", "Product / Service Compliance", 8, 0.05),
            ("LEGAL", "Legal & Commercial Readiness", 9, 0.10)
        ]
        
        for code, name, disp, weight in expected:
            existing = db.query(OppScoreSection).filter_by(section_code=code).first()
            if not existing:
                print(f"Adding section {code}")
                db.add(OppScoreSection(section_code=code, section_name=name, display_order=disp, weight=weight))
            else:
                # Update weight just in case
                existing.weight = weight
                existing.section_name = name
        
        # Ensure the demo user exists
        demo_user = db.query(AppUser).filter_by(email="sa.demo@example.com").first()
        if not demo_user:
            print("Adding demo user...")
            u = AppUser(user_id=str(uuid.uuid4()), email="sa.demo@example.com", display_name="Demo SA")
            db.add(u)
        
        db.commit()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    repair()
