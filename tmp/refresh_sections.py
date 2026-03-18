
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.models import OppScoreSection

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def refresh_sections():
    db = Session()
    try:
        REASON_OPTIONS = {
            "STRAT": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "WIN": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "FIN": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "COMP": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "FEAS": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "CUST": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "RISK": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "PROD": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] },
            "LEGAL": { "critical": [], "low": [], "average": [], "high": [], "exceptional": [] }
        }
        
        required = [
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
        
        # Clear existing ones if they are old codes
        # Actually, let's just make sure THESE exist.
        for code, name, order, weight in required:
            existing = db.query(OppScoreSection).filter_by(section_code=code).first()
            if not existing:
                print(f"Adding section {code}...")
                db.add(OppScoreSection(
                    section_code=code, 
                    section_name=name, 
                    display_order=order, 
                    weight=weight,
                    reasons=REASON_OPTIONS.get(code, {})
                ))
            else:
                print(f"Updating section {code}...")
                existing.section_name = name
                existing.display_order = order
                existing.weight = weight
        
        db.commit()
        print("✅ Opportunity sections refreshed.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    refresh_sections()
