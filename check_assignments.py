import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models import OpportunityAssignment, AppUser, Opportunity

# Database Connection
DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_data():
    db = SessionLocal()
    try:
        print("\n--- ACTIVE ASSIGNMENTS ---")
        assignments = db.query(OpportunityAssignment).filter(OpportunityAssignment.status == 'ACTIVE').all()
        
        if not assignments:
             print("No active assignments found.")
        
        for a in assignments:
            # Get User Details
            user = db.query(AppUser).filter(AppUser.user_id == a.assigned_to_user_id).first()
            opp = db.query(Opportunity).filter(Opportunity.opp_id == a.opp_id).first()
            
            print(f"AssignmentID: {a.assignment_id}")
            print(f"  > Opp: {opp.opp_name if opp else 'Unknown'} ({a.opp_id})")
            print(f"  > Assigned To: {user.display_name if user else 'Unknown'} (ID: {a.assigned_to_user_id})")
            print(f"  > Email: {user.email if user else 'Unknown Email'}")
            print("-" * 30)

        print("\n--- ALL USERS (John/Alice matches) ---")
        users = db.query(AppUser).filter(AppUser.email.in_(['john.sa@example.com', 'alice.sa@example.com'])).all()
        for u in users:
            print(f"ID: {u.user_id}, Name: {u.display_name}, Email: {u.email}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
