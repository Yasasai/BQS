
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity, UserRole, Role

db = SessionLocal()
robert = db.query(AppUser).filter(AppUser.display_name == 'Robert Chen').first()
if robert:
    roles = [ur.role.role_code for ur in robert.user_roles]
    print(f"User: {robert.display_name} (ID: {robert.user_id})")
    print(f"Roles: {roles}")
    opps = db.query(Opportunity).filter(Opportunity.assigned_sales_head_id == robert.user_id).all()
    print(f"Opportunities Assigned: {len(opps)}")
    # Check workflow status counts
    from sqlalchemy import func
    counts = db.query(Opportunity.workflow_status, func.count(Opportunity.opp_id)).filter(Opportunity.assigned_sales_head_id == robert.user_id).group_by(Opportunity.workflow_status).all()
    print(f"Status Counts: {counts}")
else:
    print("Robert Chen not found")
db.close()
