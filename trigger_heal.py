
import sys
import os

# Add project root to sys.path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from backend.app.core.database import init_db
    print("Triggering init_db()...")
    init_db()
    print("Database initialization and healing complete.")
except Exception as e:
    print(f"Error triggering heal: {e}")
