import sys
import os
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.core.database import DATABASE_URL

def inspect_db():
    print("\n--- 1. DATABASE INSPECTION ---")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check distinct workflow statuses
        print("Checking distinct workflowstatus values in DB:")
        result = conn.execute(text("SELECT workflow_status, COUNT(*) FROM opportunity GROUP BY workflow_status"))
        rows = result.fetchall()
        if not rows:
            print("  (No attempts found)")
        else:
            for row in rows:
                print(f"  '{row[0]}': {row[1]} records")
                
        # Check if any have NULL status
        result_null = conn.execute(text("SELECT COUNT(*) FROM opportunity WHERE workflow_status IS NULL"))
        null_count = result_null.scalar()
        print(f"  NULL value records: {null_count}")

def inspect_api():
    print("\n--- 2. API INSPECTION ---")
    try:
        url = "http://127.0.0.1:8000/api/opportunities/"
        print(f"Fetching from {url}...")
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"  ❌ API Error: {resp.status_code}")
            return
            
        data = resp.json()
        print(f"  ✅ API returned {len(data)} records")
        
        # Analyze the first 5 records
        print("  Sample 'workflow_status' from first 5 records:")
        for doc in data[:5]:
            print(f"    ID: {doc.get('id')} | Status: '{doc.get('workflow_status')}'")
            
        # Analyze unique statuses in API response
        statuses = {}
        for doc in data:
            s = doc.get('workflow_status')
            statuses[s] = statuses.get(s, 0) + 1
            
        print("  Distinct statuses in API response:")
        for s, count in statuses.items():
            print(f"    '{s}': {count}")
            
    except Exception as e:
        print(f"  ❌ Failed to connect to API: {e}")

if __name__ == "__main__":
    try:
        inspect_db()
        inspect_api()
    except Exception as e:
        print(f"An error occurred: {e}")
