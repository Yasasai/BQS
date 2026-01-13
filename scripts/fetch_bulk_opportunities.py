
import os
import sys
import json
from datetime import datetime

# Add project root and backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if "scripts" in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'backend'))

from backend.oracle_service import get_from_oracle

def fetch_all_screenshot_ids():
    ids = [
        "1602737", "1602738", "1693827", "1658743", "1658758", 
        "1657755", "1744044", "1754130", "1759271", "1755209", "1733846"
    ]
    
    print(f"🚀 Starting Bulk Fetch for {len(ids)} Opportunity IDs...")
    print(f"📡 Using RecordSet='ALL' for maximum visibility.\n")
    
    results = []
    
    # We can batch these in a single query for efficiency
    # Format: RecordSet='ALL';(OptyNumber='ID1' OR OptyNumber='ID2' ...)
    id_filters = " OR ".join([f"OptyNumber='{i}'" for i in ids])
    query = f"RecordSet='ALL';({id_filters})"
    
    params = {
        "q": query,
        "onlyData": "true",
        "limit": 50  # Fetching all 11 at once
    }
    
    try:
        data = get_from_oracle("opportunities", params=params)
        
        if "error" in data:
            print(f"❌ API Error: {data['error']}")
            return

        items = data.get("items", [])
        print(f"✅ Found {len(items)} out of {len(ids)} requested IDs.\n")
        
        print(f"{'ID':<10} | {'Name':<40} | {'Practice':<20} | {'Revenue':<12} | {'Win%'}")
        print("-" * 100)
        
        for item in items:
            opty_id = item.get('OptyNumber', 'N/A')
            name = item.get('Name', 'Untitled')[:40]
            # Try various practice fields
            practice = item.get('Practice_c') or item.get('Practice') or item.get('ServiceLine_c') or 'N/A'
            revenue = f"{item.get('Revenue', 0):,.0f} {item.get('CurrencyCode', '')}"
            win = f"{item.get('WinProb', 0)}%"
            
            print(f"{opty_id:<10} | {name:<40} | {practice:<20} | {revenue:<12} | {win}")
            results.append(item)

        if len(items) < len(ids):
            found_ids = [str(it.get('OptyNumber')) for it in items]
            missing = [i for i in ids if i not in found_ids]
            print(f"\n⚠️  Missing {len(missing)} IDs: {', '.join(missing)}")
            print("Suggests these specifically are still outside your user permissions.")

    except Exception as e:
        print(f"❌ Critical Failure: {e}")

if __name__ == "__main__":
    fetch_all_screenshot_ids()
