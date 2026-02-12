"""
Quick script to create users via the API endpoint
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

users_to_create = [
    # Global Heads
    {"email": "james.wilson@company.com", "display_name": "James Wilson", "roles": ["GH"]},
    {"email": "maria.garcia@company.com", "display_name": "Maria Garcia", "roles": ["GH"]},
    
    # Practice Heads
    {"email": "sarah.mitchell@company.com", "display_name": "Sarah Mitchell", "roles": ["PH"]},
    {"email": "david.chen@company.com", "display_name": "David Chen", "roles": ["PH"]},
    {"email": "priya.sharma@company.com", "display_name": "Priya Sharma", "roles": ["PH"]},
    {"email": "michael.brown@company.com", "display_name": "Michael Brown", "roles": ["PH"]},
    {"email": "lisa.anderson@company.com", "display_name": "Lisa Anderson", "roles": ["PH"]},
    
    # Sales Heads
    {"email": "robert.chen@company.com", "display_name": "Robert Chen", "roles": ["SH"]},
    {"email": "jennifer.lee@company.com", "display_name": "Jennifer Lee", "roles": ["SH"]},
    {"email": "alex.kumar@company.com", "display_name": "Alex Kumar", "roles": ["SH"]},
    {"email": "emma.johnson@company.com", "display_name": "Emma Johnson", "roles": ["SH"]},
    
    # Solution Architects
    {"email": "john.doe@company.com", "display_name": "John Doe", "roles": ["SA"]},
    {"email": "alice.wong@company.com", "display_name": "Alice Wong", "roles": ["SA"]},
    {"email": "raj.patel@company.com", "display_name": "Raj Patel", "roles": ["SA"]},
    {"email": "sophia.martinez@company.com", "display_name": "Sophia Martinez", "roles": ["SA"]},
    {"email": "thomas.wright@company.com", "display_name": "Thomas Wright", "roles": ["SA"]},
    {"email": "olivia.taylor@company.com", "display_name": "Olivia Taylor", "roles": ["SA"]},
    
    # Salespersons
    {"email": "emily.white@company.com", "display_name": "Emily White", "roles": ["SP"]},
    {"email": "daniel.kim@company.com", "display_name": "Daniel Kim", "roles": ["SP"]},
    {"email": "natalie.rodriguez@company.com", "display_name": "Natalie Rodriguez", "roles": ["SP"]},
    {"email": "kevin.nguyen@company.com", "display_name": "Kevin Nguyen", "roles": ["SP"]},
    {"email": "hannah.davis@company.com", "display_name": "Hannah Davis", "roles": ["SP"]},
]

print("🌱 Creating users via API...")
print("=" * 50)

created = 0
skipped = 0
errors = 0

for user_data in users_to_create:
    try:
        response = requests.post(
            f"{API_BASE}/api/auth/users",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Created: {user_data['display_name']} ({user_data['roles'][0]})")
            created += 1
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"ℹ️  Skipped: {user_data['display_name']} (already exists)")
            skipped += 1
        else:
            print(f"❌ Error creating {user_data['display_name']}: {response.status_code} - {response.text}")
            errors += 1
    except Exception as e:
        print(f"❌ Exception creating {user_data['display_name']}: {e}")
        errors += 1

print("=" * 50)
print(f"\n📊 Summary:")
print(f"  Created: {created}")
print(f"  Skipped: {skipped}")
print(f"  Errors:  {errors}")
print(f"  Total:   {len(users_to_create)}")

if errors == 0:
    print("\n✅ All users processed successfully!")
    print("\n🔑 You can now test the assignment modal!")
else:
    print(f"\n⚠️  {errors} errors occurred. Check the output above.")
