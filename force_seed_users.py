import sys
import os
import uuid
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add path
sys.path.append(os.getcwd())

try:
    from backend.app.core.database import DATABASE_URL
    from backend.app.models import AppUser, Role, UserRole
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)

def seed():
    logger.info(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Ensure Role
        sa_role = session.query(Role).filter_by(role_code='SA').first()
        if not sa_role:
            logger.info("Creating SA role...")
            sa_role = Role(role_id=2, role_code='SA', role_name='Solution Architect')
            session.add(sa_role)
            session.commit()
        
        # 2. Ensure Users
        users_data = [
            ("alice.sa@example.com", "Alice Architect"),
            ("bob.sa@example.com", "Bob Builder")
        ]

        for email, name in users_data:
            user = session.query(AppUser).filter_by(email=email).first()
            if not user:
                logger.info(f"Creating user {name}...")
                user = AppUser(user_id=str(uuid.uuid4()), email=email, display_name=name, is_active=True)
                session.add(user)
                session.commit()
            
            # 3. Ensure Assignment
            ur = session.query(UserRole).filter_by(user_id=user.user_id, role_id=sa_role.role_id).first()
            if not ur:
                logger.info(f"Assigning SA role to {name}...")
                ur = UserRole(user_id=user.user_id, role_id=sa_role.role_id)
                session.add(ur)
                session.commit()
            else:
                logger.info(f"{name} is correctly configured.")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed()
