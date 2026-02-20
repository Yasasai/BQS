
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from backend.database import SessionLocal, Opportunity
db = SessionLocal()
count = db.query(Opportunity).count()
print(f"DEBUG: Opportunities count = {count}")
db.close()
