
import os
import sys

# Add root directory to path
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import Opportunity
db = SessionLocal()
count = db.query(Opportunity).count()
print(f"DEBUG: Opportunities count in app.models = {count}")
db.close()
