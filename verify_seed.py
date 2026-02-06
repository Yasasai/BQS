import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from backend.app.models import Role, OppScoreSection
from backend.app.core.database import SessionLocal

def check_data():
    db = SessionLocal()
    try:
        print("🔍 Verifying Data...")
        
        roles = db.query(Role).all()
        print(f"Roles found: {[r.role_code for r in roles]}")
        
        sections = db.query(OppScoreSection).all()
        print(f"Sections found: {[s.section_code for s in sections]}")

    finally:
        db.close()

if __name__ == "__main__":
    check_data()
