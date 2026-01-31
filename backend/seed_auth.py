import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db

print("Running database initialization to seed PH_001 and SA_001...")
try:
    init_db()
    print("Seeding complete.")
except Exception as e:
    print(f"Error: {e}")
