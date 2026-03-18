import os
from dotenv import load_dotenv
import uuid
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

load_dotenv() 

def seed():
    db = SessionLocal()
    try:
        # Get SH and SA users
        sh_user = db.query(AppUser).filter(AppUser.display_name.ilike('%SH%') | AppUser.display_name.ilike('%Sales Head%') | AppUser.email.ilike('%sh%')).first()
        sa_user = db.query(AppUser).filter(AppUser.display_name.ilike('%SA%') | AppUser.display_name.ilike('%Solution Architect%') | AppUser.email.ilike('%sa%')).first()
        
        # We know from earlier phase seeded data uses 'Sarah' as SA and 'Sam' as SH commonly, let's just query by role if needed or by known emails.
        # Let's query based on Role to be safer.
        from backend.app.models import UserRole, Role
        
        sh_role = db.query(Role).filter(Role.role_code == 'SH').first()
        sa_role = db.query(Role).filter(Role.role_code == 'SA').first()
        
        if sh_role:
            sh_ur = db.query(UserRole).filter(UserRole.role_id == sh_role.role_id).first()
            if sh_ur: sh_user = db.query(AppUser).filter(AppUser.user_id == sh_ur.user_id).first()
        
        if sa_role:
            sa_ur = db.query(UserRole).filter(UserRole.role_id == sa_role.role_id).first()
            if sa_ur: sa_user = db.query(AppUser).filter(AppUser.user_id == sa_ur.user_id).first()
            
        if not sh_user:
            print("SH user not found, defaulting...")
            sh_user = db.query(AppUser).first()
        if not sa_user:
            print("SA user not found, defaulting...")
            sa_user = db.query(AppUser).filter(AppUser.user_id != sh_user.user_id).first()
            
        print(f"Assigning SH: {sh_user.email} (ID: {sh_user.user_id})")
        print(f"Assigning SA: {sa_user.email} (ID: {sa_user.user_id})")

        opps = db.query(Opportunity).order_by(Opportunity.opp_id).limit(20).all()
        
        for i, opp in enumerate(opps):
            opp.sales_owner_user_id = sh_user.user_id
            opp.assigned_sales_head_id = sh_user.user_id
            
            if i < 5:
                opp.assigned_sa_id = sa_user.user_id
                opp.workflow_status = 'ASSIGNED_TO_SA'
                
        db.commit()
        print(f"Successfully updated {len(opps)} opportunities.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
