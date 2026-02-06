import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from backend.app.models import Base, Role, AppUser, UserRole, OppScoreSection
from backend.app.core.database import SessionLocal
from sqlalchemy.orm import Session

def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding Prototype Roles and Sections...")

        # 1. SEED ROLES
        roles = [
            {"role_id": 101, "role_code": "GH", "role_name": "Global Head"},
            {"role_id": 102, "role_code": "PH", "role_name": "Practice Head"},
            {"role_id": 103, "role_code": "SH", "role_name": "Sales Head"},
            {"role_id": 104, "role_code": "SA", "role_name": "Solution Architect"},
            {"role_id": 105, "role_code": "SP", "role_name": "Sales Presales"},
        ]

        for r_data in roles:
            existing = db.query(Role).filter(Role.role_code == r_data["role_code"]).first()
            if not existing:
                new_role = Role(**r_data)
                db.add(new_role)
                print(f"   [+] Added Role: {r_data['role_code']}")
            else:
                print(f"   [.] Role exists: {r_data['role_code']}")
        
        db.commit()

        # 2. SEED SECTIONS
        sections = [
            {"section_code": "strategic_fit", "section_name": "Strategic Fit", "weight": 0.15, "display_order": 1},
            {"section_code": "win_probability", "section_name": "Win Probability", "weight": 0.15, "display_order": 2},
            {"section_code": "financial_value", "section_name": "Financial Value", "weight": 0.15, "display_order": 3},
            {"section_code": "competitive_position", "section_name": "Competitive Position", "weight": 0.10, "display_order": 4},
            {"section_code": "delivery_feasibility", "section_name": "Delivery Feasibility", "weight": 0.10, "display_order": 5},
            {"section_code": "customer_relationship", "section_name": "Customer Relationship", "weight": 0.10, "display_order": 6},
            {"section_code": "risk_exposure", "section_name": "Risk Exposure", "weight": 0.10, "display_order": 7},
            {"section_code": "compliance", "section_name": "Product / Service Compliance", "weight": 0.05, "display_order": 8},
            {"section_code": "legal_readiness", "section_name": "Legal & Commercial Readiness", "weight": 0.10, "display_order": 9},
        ]

        for s_data in sections:
            existing = db.query(OppScoreSection).filter(OppScoreSection.section_code == s_data["section_code"]).first()
            if existing: # Update
                existing.section_name = s_data["section_name"]
                existing.weight = s_data["weight"]
                existing.display_order = s_data["display_order"]
                print(f"   [U] Updated Section: {s_data['section_code']}")
            else:
                new_section = OppScoreSection(**s_data)
                db.add(new_section)
                print(f"   [+] Added Section: {s_data['section_code']}")
        
        db.commit()
        print("✅ Seeding Complete.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
