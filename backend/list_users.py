
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, UserRole, Role

db = SessionLocal()
users = db.query(AppUser).all()
print("ID | Name | Roles")
print("-" * 30)
for u in users:
    roles = [ur.role.role_code for ur in u.user_roles]
    print(f"{u.user_id} | {u.display_name} | {roles}")
db.close()
