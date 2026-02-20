
import os
import sys
# Path setup
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal
from backend.app.models import OracleOpportunity

try:
    db = SessionLocal()
    count = db.query(OracleOpportunity).count()
    with open("current_count.txt", "w") as f:
        f.write(str(count))
    db.close()
    print(f"COUNT_SUCCESS: {count}")
except Exception as e:
    with open("current_count_error.txt", "w") as f:
        f.write(str(e))
    print(f"COUNT_ERROR: {e}")
