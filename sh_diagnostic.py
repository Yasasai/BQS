
import sys
import os

# Change to project root
os.chdir(r"c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS")
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Role, UserRole, Opportunity

def diagnostic():
    db = SessionLocal()
    with open("sh_diagnostic_log.txt", "w") as f:
        f.write("--- SH DIAGNOSTIC ---\n")
        
        # 1. Check SH User
        sh = db.query(AppUser).filter(AppUser.user_id == 'sh-001').first()
        f.write(f"Sales Head (sh-001): {sh.display_name if sh else 'MISSING'}\n")
        
        # 2. Check SP Users
        sp_role = db.query(Role).filter(Role.role_code == 'SP').first()
        f.write(f"SP Role exists: {sp_role is not None}\n")
        if sp_role:
            sp_users = db.query(AppUser).join(UserRole).filter(UserRole.role_id == sp_role.role_id).all()
            f.write(f"SP Users found: {[u.display_name for u in sp_users]}\n")
            for u in sp_users:
                f.write(f"  - {u.display_name} (ID: {u.user_id}, Email: {u.email})\n")
        
        # 3. Check Opportunities assigned to SH
        sh_opps = db.query(Opportunity).filter(Opportunity.assigned_sales_head_id == 'sh-001').all()
        f.write(f"Opportunities assigned to SH: {len(sh_opps)}\n")
        for o in sh_opps:
            f.write(f"  - {o.opp_id} | Name: {o.opp_name} | Assigned SP ID: {o.assigned_sp_id} | Status: {o.workflow_status}\n")

    db.close()

if __name__ == "__main__":
    diagnostic()
