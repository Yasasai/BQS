import sys
import os

sys.path.append(r'C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS')
print(f"Python Path: {sys.path}")

try:
    print("Importing opportunities...")
    from backend.app.routers import opportunities
    print("Opportunities imported successfully.")
    
    print("Importing scoring...")
    from backend.app.routers import scoring
    print("Scoring imported successfully.")
    
except Exception as e:
    print(f"FAILED: {e}")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
