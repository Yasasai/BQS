from backend.app.core.database import get_db
from backend.app.models import Opportunity

db = next(get_db())
opps = db.query(Opportunity).all()

print(f"\n{'='*60}")
print(f"Total opportunities in database: {len(opps)}")
print(f"{'='*60}\n")

if len(opps) > 0:
    print("First 10 opportunities:")
    for i, o in enumerate(opps[:10], 1):
        print(f"{i}. {o.opp_name}")
        print(f"   Customer: {o.customer_name}")
        print(f"   Value: ${o.deal_value or 0}")
        print(f"   Status: {o.workflow_status or 'NEW'}")
        print()
else:
    print("⚠️  No opportunities found in the database!")
    print("You may need to run the Oracle sync to fetch opportunities.")
