
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.models import Role, AppUser, UserRole

DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def fix_roles():
    db = Session()
    try:
        # 1. Check if roles exist
        bm_role = db.query(Role).filter(Role.role_code == 'BM').first()
        if not bm_role:
            print("Creating BM (Bid Manager) role...")
            bm_role = Role(role_id=10, role_code='BM', role_name='Bid Manager')
            db.merge(bm_role)
            
        sl_role = db.query(Role).filter(Role.role_code == 'SL').first()
        if not sl_role:
            print("Creating SL (Sales Lead) role...")
            sl_role = Role(role_id=11, role_code='SL', role_name='Sales Lead')
            db.merge(sl_role)
        
        db.commit()
        print("✅ Roles created/verified.")

        # 2. Assign BM to an elective user if no one has it
        # Let's check who is supposed to be the BM
        # From seed_users.py, SA John Doe (sa-001) or SP Emily White (sp-001)
        # The user says "displayed as a Bid Manager", so maybe they already have it?
        
        # Let's look for any user with name containing 'Bid Manager'
        bm_user = db.query(AppUser).filter(AppUser.display_name.ilike('%Bid Manager%')).first()
        if bm_user:
            print(f"Found user {bm_user.display_name}. Assigning BM role...")
            # Check if already assigned
            exists = db.query(UserRole).filter_by(user_id=bm_user.user_id, role_id=bm_role.role_id).first()
            if not exists:
                db.add(UserRole(user_id=bm_user.user_id, role_id=bm_role.role_id))
        
        # Assign SL to Robert Chen (sh-001) or similar
        robert = db.query(AppUser).filter_by(user_id='sh-001').first()
        if not robert:
             robert = db.query(AppUser).filter(AppUser.display_name.ilike('%Robert%')).first()
             
        if robert:
            print(f"Assigning SL role to {robert.display_name}...")
            exists = db.query(UserRole).filter_by(user_id=robert.user_id, role_id=sl_role.role_id).first()
            if not exists:
                db.add(UserRole(user_id=robert.user_id, role_id=sl_role.role_id))
        
        # Also assign BM to John Doe (sa-001) for testing
        john = db.query(AppUser).filter_by(user_id='sa-001').first()
        if john:
            print(f"Assigning BM role to John Doe...")
            exists = db.query(UserRole).filter_by(user_id=john.user_id, role_id=bm_role.role_id).first()
            if not exists:
                db.add(UserRole(user_id=john.user_id, role_id=bm_role.role_id))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_roles()
