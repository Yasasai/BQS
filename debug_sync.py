import sys
import traceback
sys.path.append('.')
from backend.app.core.database import SessionLocal, init_db
from backend.app.services.sync_manager import sync_opportunities, map_oracle_to_db, ORACLE_BASE_URL, ORACLE_USER, ORACLE_PASSWORD
import httpx
print("Starting debug script...")

init_db()
db = SessionLocal()

limit = 10
offset = 0

url = f"{ORACLE_BASE_URL}/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&limit={limit}&offset={offset}"
print("Fetching URL:", url)

with httpx.Client(auth=(ORACLE_USER, ORACLE_PASSWORD), timeout=60.0) as client:
    response = client.get(url)
    items = response.json().get("items", [])
    print(f"Found {len(items)} items")
    for item in items:
        try:
            mapped = map_oracle_to_db(item, db)
            if mapped:
                from backend.app.models import Opportunity
                existing = db.query(Opportunity).filter(Opportunity.opp_id == mapped["opp_id"]).first()
                if existing:
                    for k, v in mapped.items():
                        setattr(existing, k, v)
                else:
                    db.add(Opportunity(**mapped))
                db.commit()
                print("Saved:", mapped["opp_id"])
        except Exception as e:
            print(f"FAILED on item {item.get('OptyId')}: {e}")
            sys.excepthook(*sys.exc_info())
            db.rollback()
