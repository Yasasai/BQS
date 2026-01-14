"""
Oracle Opportunity Fetcher by Name
Fetches opportunities using their visible names from the dashboard
"""
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import SessionLocal, Opportunity, OpportunityDetails, init_db

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Credentials
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASS = os.getenv("ORACLE_PASSWORD", "")
BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com") + "/crmRestApi/resources/latest"

if not ORACLE_USER or not ORACLE_PASS:
    print("❌ ERROR: ORACLE_USER and ORACLE_PASSWORD must be set in .env file")
    sys.exit(1)

def fetch_by_name(opty_name):
    """
    Fetch a single opportunity by its Name (visible in dashboard)
    """
    url = f"{BASE_URL}/opportunities"
    
    # Use query parameter to search by Name
    params = {
        "q": f"Name='{opty_name}'",
        "onlyData": "true",
        "limit": 1
    }
    
    try:
        r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
        
        if r.status_code == 404:
            print(f"❌ 404 Error - Endpoint not found. Trying alternate URL...")
            # Try without 'latest'
            url = "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.13.18.05/opportunities"
            r = requests.get(url, auth=HTTPBasicAuth(ORACLE_USER, ORACLE_PASS), params=params, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            items = data.get("items", [])
            if items:
                return items[0]
            else:
                print(f"⚠️  No opportunity found with name: {opty_name}")
                return None
        else:
            print(f"❌ Error {r.status_code}: {r.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def fetch_multiple_by_names(name_list):
    """
    Fetch multiple opportunities by their names
    name_list: List of opportunity names from the dashboard
    """
    print(f"🔍 Fetching {len(name_list)} opportunities by name...\n")
    
    results = []
    for idx, name in enumerate(name_list, 1):
        print(f"[{idx}/{len(name_list)}] Fetching: {name}")
        opty = fetch_by_name(name)
        if opty:
            results.append(opty)
            print(f"   ✅ Found: OptyNumber={opty.get('OptyNumber')}, Revenue={opty.get('Revenue')}")
        else:
            print(f"   ❌ Not found")
    
    return results

def save_to_db(opportunities):
    """Save fetched opportunities to PostgreSQL"""
    if not opportunities:
        print("\n⚠️  No opportunities to save.")
        return
    
    print(f"\n💾 Saving {len(opportunities)} opportunities to database...")
    init_db()  # Ensure schema is up to date
    
    db = SessionLocal()
    try:
        from oracle_service import map_oracle_to_db
        
        for opty in opportunities:
            try:
                mapped = map_oracle_to_db(opty)
                if not mapped:
                    continue
                
                remote_id = mapped['primary']['remote_id']
                
                # Check if exists
                existing = db.query(Opportunity).filter(Opportunity.remote_id == remote_id).first()
                
                if existing:
                    # Update
                    for key, val in mapped['primary'].items():
                        setattr(existing, key, val)
                    print(f"   ✅ Updated: {remote_id}")
                else:
                    # Create new
                    new_opp = Opportunity(**mapped['primary'], workflow_status='NEW', status='New from CRM')
                    db.add(new_opp)
                    print(f"   ✅ Created: {remote_id}")
                
                # Save details
                existing_details = db.query(OpportunityDetails).filter(
                    OpportunityDetails.opty_number == remote_id
                ).first()
                
                if existing_details:
                    for key, val in mapped['details'].items():
                        setattr(existing_details, key, val)
                else:
                    new_details = OpportunityDetails(**mapped['details'])
                    db.add(new_details)
                
            except Exception as e:
                print(f"   ❌ Error saving {opty.get('Name')}: {e}")
                continue
        
        db.commit()
        print(f"\n🎉 Successfully saved {len(opportunities)} opportunities!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # STEP 1: Add your opportunity names from the dashboard here
    # Copy-paste the names you see in the Oracle UI
    opportunity_names = [
        "16985449 IAM with Sailsource 12m offsh",  # Example from your screenshot
        "1602737 SAS Media test PZ Cloud v 2 0",   # Example from your screenshot
        "1553327 revised1 IMR DDock V 2 3",        # Example from your screenshot
        # Add more names here...
    ]
    
    print("=" * 60)
    print("Oracle Opportunity Fetcher by Name")
    print("=" * 60)
    
    # STEP 2: Fetch opportunities
    opportunities = fetch_multiple_by_names(opportunity_names)
    
    # STEP 3: Save to database
    if opportunities:
        save_to_db(opportunities)
        
        # STEP 4: Show summary
        print("\n📊 SUMMARY:")
        print(f"Total fetched: {len(opportunities)}")
        print(f"Total in name list: {len(opportunity_names)}")
        print(f"Success rate: {len(opportunities)/len(opportunity_names)*100:.1f}%")
    else:
        print("\n❌ No opportunities were fetched. Check:")
        print("1. The opportunity names are exact matches")
        print("2. Your user has permission to view these opportunities")
        print("3. The API endpoint is correct")
