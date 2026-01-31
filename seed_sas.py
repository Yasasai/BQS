import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal, init_db
from backend.app.models import AppUser, Role, UserRole

def seed_users():
    with open("seed_log.txt", "w") as log:
        log.write("Starting Seeding...\n")
        try:
            db = SessionLocal()
            log.write("DB Connection Opened\n")

            # Roles
            sa_role = db.query(Role).filter_by(role_code='SA').first()
            if not sa_role:
                sa_role = Role(role_id=2, role_code='SA', role_name='Solution Architect')
                db.add(sa_role)
                log.write("Created SA Role\n")
            
            ph_role = db.query(Role).filter_by(role_code='PRACTICE_HEAD').first()
            if not ph_role:
                ph_role = Role(role_id=1, role_code='PRACTICE_HEAD', role_name='Practice Head')
                db.add(ph_role)
                log.write("Created PH Role\n")

            db.commit()

            users_to_seed = [
                {"id": "SA_001", "name": "Alice", "email": "alice.sa@example.com", "role": sa_role},
                {"id": "SA_002", "name": "John", "email": "john.sa@example.com", "role": sa_role},
                 {"id": "PH_001", "name": "Sarah PracticeHead", "email": "sarah.ph@example.com", "role": ph_role}
            ]

            for u_data in users_to_seed:
                # Check by EMAIL first to avoid duplicates with different IDs
                existing_email = db.query(AppUser).filter_by(email=u_data["email"]).first()
                if existing_email:
                    log.write(f"User email exists: {u_data['email']}\n")
                    user = existing_email
                else:
                    # Check by ID
                    user = db.query(AppUser).filter_by(user_id=u_data["id"]).first()
                
                if not user:
                    user = AppUser(
                        user_id=u_data["id"],
                        display_name=u_data["name"],
                        email=u_data["email"],
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    
                    ur = UserRole(user_id=user.user_id, role_id=u_data["role"].role_id)
                    db.add(ur)
                    log.write(f"Created User: {u_data['name']}\n")
                else:
                    log.write(f"User exists: {u_data['name']}\n")
                    user.display_name = u_data["name"] # FORCE UPDATE NAME
                    db.add(user)
                    
                    has_role = db.query(UserRole).filter_by(user_id=user.user_id, role_id=u_data["role"].role_id).first()
                    if not has_role:
                        ur = UserRole(user_id=user.user_id, role_id=u_data["role"].role_id)
                        db.add(ur)
                        log.write(f"Added role to: {u_data['name']}\n")

            db.commit()
            log.write("Seeding Complete\n")

        except Exception as e:
            log.write(f"Error: {e}\n")
            import traceback
            log.write(traceback.format_exc())
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    seed_users()
