import sys
import traceback
from app.core.database import SessionLocal
from app.services.opportunity_service import get_paginated_opportunities_logic

def main():
    try:
        db = SessionLocal()
        print("db session created")
        res = get_paginated_opportunities_logic(db=db, user_id="gh-001", role="GH")
        print("Success:", res)
    except Exception as e:
        print("CAUGHT EXCEPTION:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
