
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.models import Role, AppUser, UserRole

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

roles = db.query(Role).all()
with open("roles_dump.txt", "w") as f:
    f.write("ROLES:\n")
    for r in roles:
        f.write(f"ID: {r.role_id}, Code: {r.role_code}, Name: {r.role_name}\n")
    
    f.write("\nUSERS AND ROLES:\n")
    users = db.query(AppUser).all()
    for u in users:
        rcodes = [ur.role.role_code for ur in u.user_roles]
        f.write(f"User: {u.display_name} ({u.email}), Roles: {rcodes}\n")

db.close()
