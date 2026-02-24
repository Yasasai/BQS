
from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
import json

db = SessionLocal()
results = {}

# Sarah
sarah_opps = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-001').all()
results['sarah'] = {
    'total': len(sarah_opps),
    'no_sa': len([o for o in sarah_opps if not o.assigned_sa_id]),
    'has_sa': len([o for o in sarah_opps if o.assigned_sa_id]),
    'workflow_statuses': list(set([o.workflow_status for o in sarah_opps]))
}

# David
david_opps = db.query(Opportunity).filter(Opportunity.assigned_practice_head_id == 'ph-002').all()
results['david'] = {
    'total': len(david_opps),
    'no_sa': len([o for o in david_opps if not o.assigned_sa_id])
}

# General
results['general'] = {
    'total': db.query(Opportunity).count(),
    'unassigned_ph': db.query(Opportunity).filter(Opportunity.assigned_practice_head_id.is_(None)).count()
}

print(json.dumps(results, indent=2))
db.close()
