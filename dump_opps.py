
import sys
import os
import json
from datetime import datetime

sys.path.append(os.getcwd())
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity

def my_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

db = SessionLocal()
opps = db.query(Opportunity).all()
results = []
for o in opps:
    results.append({
        "id": o.opp_id,
        "name": o.opp_name,
        "status": o.workflow_status,
        "assigned_sa": o.sales_owner_user_id # Note: Model field is sales_owner_user_id, wait.
    })

# In the model:
# sales_owner_user_id is the SALES OWNER (e.g. from CRM).
# assigned_sa (in API) comes from OpportunityAssignment.

# Let's verify OpportunityAssignment
from backend.app.models import OpportunityAssignment
assigns = db.query(OpportunityAssignment).filter(OpportunityAssignment.status == 'ACTIVE').all()
active_map = {}
for a in assigns:
    active_map[a.opp_id] = a.assigned_to_user_id

final_dump = []
for o in opps:
    assigned_user = active_map.get(o.opp_id, "UNASSIGNED")
    final_dump.append({
        "id": o.opp_id,
        "name": o.opp_name,
        "db_status": o.workflow_status,
        "active_assignment_user": assigned_user
    })

with open("opp_dump.json", "w") as f:
    json.dump(final_dump, f, default=my_converter, indent=2)

print("Dumped to opp_dump.json")
db.close()
