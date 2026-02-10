"""
Seed script to populate users for all roles in the BQS system.
This creates dummy users for testing the assignment workflow.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from app.models import AppUser, Role, UserRole, Base

def seed_users():
    """Seed the database with test users for all roles"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🌱 Starting user seeding process...")
        
        # Step 1: Create/Update Roles
        print("\n📋 Creating roles...")
        roles_data = [
            {"role_id": 1, "role_code": "GH", "role_name": "Global Head"},
            {"role_id": 2, "role_code": "PH", "role_name": "Practice Head"},
            {"role_id": 3, "role_code": "SH", "role_name": "Sales Head"},
            {"role_id": 4, "role_code": "SA", "role_name": "Solution Architect"},
            {"role_id": 5, "role_code": "SP", "role_name": "Salesperson"},
        ]
        
        for role_data in roles_data:
            role = db.query(Role).filter(Role.role_code == role_data["role_code"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                print(f"  ✅ Created role: {role_data['role_name']}")
            else:
                print(f"  ℹ️  Role already exists: {role_data['role_name']}")
        
        db.commit()
        
        # Step 2: Create Users
        print("\n👥 Creating users...")
        
        users_data = [
            # Global Heads
            {"user_id": "gh-001", "email": "james.wilson@company.com", "display_name": "James Wilson", "role_code": "GH"},
            {"user_id": "gh-002", "email": "maria.garcia@company.com", "display_name": "Maria Garcia", "role_code": "GH"},
            
            # Practice Heads
            {"user_id": "ph-001", "email": "sarah.mitchell@company.com", "display_name": "Sarah Mitchell", "role_code": "PH"},
            {"user_id": "ph-002", "email": "david.chen@company.com", "display_name": "David Chen", "role_code": "PH"},
            {"user_id": "ph-003", "email": "priya.sharma@company.com", "display_name": "Priya Sharma", "role_code": "PH"},
            {"user_id": "ph-004", "email": "michael.brown@company.com", "display_name": "Michael Brown", "role_code": "PH"},
            {"user_id": "ph-005", "email": "lisa.anderson@company.com", "display_name": "Lisa Anderson", "role_code": "PH"},
            
            # Sales Heads
            {"user_id": "sh-001", "email": "robert.chen@company.com", "display_name": "Robert Chen", "role_code": "SH"},
            {"user_id": "sh-002", "email": "jennifer.lee@company.com", "display_name": "Jennifer Lee", "role_code": "SH"},
            {"user_id": "sh-003", "email": "alex.kumar@company.com", "display_name": "Alex Kumar", "role_code": "SH"},
            {"user_id": "sh-004", "email": "emma.johnson@company.com", "display_name": "Emma Johnson", "role_code": "SH"},
            
            # Solution Architects
            {"user_id": "sa-001", "email": "john.doe@company.com", "display_name": "John Doe", "role_code": "SA"},
            {"user_id": "sa-002", "email": "alice.wong@company.com", "display_name": "Alice Wong", "role_code": "SA"},
            {"user_id": "sa-003", "email": "raj.patel@company.com", "display_name": "Raj Patel", "role_code": "SA"},
            {"user_id": "sa-004", "email": "sophia.martinez@company.com", "display_name": "Sophia Martinez", "role_code": "SA"},
            {"user_id": "sa-005", "email": "thomas.wright@company.com", "display_name": "Thomas Wright", "role_code": "SA"},
            {"user_id": "sa-006", "email": "olivia.taylor@company.com", "display_name": "Olivia Taylor", "role_code": "SA"},
            
            # Salespersons
            {"user_id": "sp-001", "email": "emily.white@company.com", "display_name": "Emily White", "role_code": "SP"},
            {"user_id": "sp-002", "email": "daniel.kim@company.com", "display_name": "Daniel Kim", "role_code": "SP"},
            {"user_id": "sp-003", "email": "natalie.rodriguez@company.com", "display_name": "Natalie Rodriguez", "role_code": "SP"},
            {"user_id": "sp-004", "email": "kevin.nguyen@company.com", "display_name": "Kevin Nguyen", "role_code": "SP"},
            {"user_id": "sp-005", "email": "hannah.davis@company.com", "display_name": "Hannah Davis", "role_code": "SP"},
        ]
        
        for user_data in users_data:
            # Check if user exists
            user = db.query(AppUser).filter(AppUser.user_id == user_data["user_id"]).first()
            
            if not user:
                # Create user
                user = AppUser(
                    user_id=user_data["user_id"],
                    email=user_data["email"],
                    display_name=user_data["display_name"],
                    is_active=True
                )
                db.add(user)
                db.flush()  # Get the user_id
                print(f"  ✅ Created user: {user_data['display_name']} ({user_data['role_code']})")
            else:
                print(f"  ℹ️  User already exists: {user_data['display_name']}")
            
            # Assign role
            role = db.query(Role).filter(Role.role_code == user_data["role_code"]).first()
            if role:
                # Check if user_role already exists
                user_role = db.query(UserRole).filter(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id
                ).first()
                
                if not user_role:
                    user_role = UserRole(user_id=user.user_id, role_id=role.role_id)
                    db.add(user_role)
                    print(f"    → Assigned role: {user_data['role_code']}")
        
        db.commit()
        
        # Step 3: Verify and display summary
        print("\n📊 Seeding Summary:")
        print("=" * 50)
        
        for role_data in roles_data:
            role = db.query(Role).filter(Role.role_code == role_data["role_code"]).first()
            if role:
                count = db.query(UserRole).filter(UserRole.role_id == role.role_id).count()
                print(f"  {role_data['role_name']:20} : {count} users")
        
        total_users = db.query(AppUser).count()
        print(f"\n  {'Total Users':20} : {total_users}")
        print("=" * 50)
        
        print("\n✅ User seeding completed successfully!")
        print("\n📝 You can now:")
        print("  1. Login as any user using their email")
        print("  2. Assign opportunities to Practice Heads and Sales Heads")
        print("  3. Test the complete workflow")
        
        print("\n🔑 Sample logins:")
        print("  Global Head    : james.wilson@company.com")
        print("  Practice Head  : sarah.mitchell@company.com")
        print("  Sales Head     : robert.chen@company.com")
        print("  Solution Arch  : john.doe@company.com")
        print("  Salesperson    : emily.white@company.com")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
