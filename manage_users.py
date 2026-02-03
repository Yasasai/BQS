import sys
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import DATABASE_URL
from backend.app.models import AppUser, Role, UserRole

def create_users():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Ensure SA Role
        sa_role = session.query(Role).filter_by(role_code='SA').first()
        if not sa_role:
            print("Creating SA Role...")
            sa_role = Role(role_id=2, role_code='SA', role_name='Solution Architect')
            session.add(sa_role)
            session.commit()
        else:
            print(f"Role SA exists (ID: {sa_role.role_id})")

        # 2. Create Dummy Users
        dummies = [
            {"email": "alice.sa@example.com", "name": "Alice Architect"},
            {"email": "bob.sa@example.com", "name": "Bob Builder"}
        ]

        for d in dummies:
            user = session.query(AppUser).filter_by(email=d['email']).first()
            if not user:
                print(f"Creating user {d['name']}...")
                user = AppUser(
                    user_id=str(uuid.uuid4()),
                    email=d['email'],
                    display_name=d['name'],
                    is_active=True
                )
                session.add(user)
                session.commit()
            else:
                print(f"User {d['name']} exists.")

            # 3. Assign Role
            user_role = session.query(UserRole).filter_by(user_id=user.user_id, role_id=sa_role.role_id).first()
            if not user_role:
                print(f"Assigning SA role to {d['name']}...")
                ur = UserRole(user_id=user.user_id, role_id=sa_role.role_id)
                session.add(ur)
                session.commit()
            else:
                print(f"User {d['name']} already has SA role.")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_users()
