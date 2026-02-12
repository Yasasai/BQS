
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from backend.app.core.database import SessionLocal
from backend.app.models import AppUser, Opportunity

def check_sh_assignments():
    db = SessionLocal()
    try:
        sh_id = 'sh-001' # Robert Chen
        sh = db.query(AppUser).filter(AppUser.user_id == sh_id).first()
        if not sh:
            print(f"❌ User '{sh_id}' not found.")
            return
            
        print(f"✅ Found SH: {sh.display_name}")
        
        count = db.query(Opportunity).filter(Opportunity.assigned_sales_head_id == sh_id).count()
        print(f"📊 Opportunities assigned to SH: {count}")
        
        if count == 0:
            print("⚠️ SH has zero assignments. I should assign some.")
    finally:
        db.close()

if __name__ == "__main__":
    check_sh_assignments()
