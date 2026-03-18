from app.core.database import SessionLocal
from app.services.opportunity_service import get_paginated_opportunities_logic
try:
    db = SessionLocal()
    get_paginated_opportunities_logic(db=db, user_id="gh-001", role="GH")
except Exception as e:
    import traceback
    traceback.print_exc()
