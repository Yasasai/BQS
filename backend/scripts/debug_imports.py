import sys
import os

# Add parent directory to path to import app modules
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
print(f"Base path added: {base_path}")

try:
    from app.models import Base
    print("Successfully imported Base from app.models")
except Exception as e:
    print(f"Failed to import: {e}")
