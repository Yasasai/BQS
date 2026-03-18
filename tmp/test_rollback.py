
import sys
import os
from unittest.mock import MagicMock

# Mock sqlalchemy and other dependencies
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['backend.app.core.database'] = MagicMock()
sys.modules['backend.app.models'] = MagicMock()
sys.modules['backend.app.core.logging_config'] = MagicMock()

# Import the function after mocking
from backend.app.services.sync_manager import map_oracle_to_db

def test_rollback_on_error():
    db_mock = MagicMock()
    # Force an error in Practice query to trigger the except block
    db_mock.query.side_effect = Exception("Forced DB Error")
    
    item = {"OptyId": "123", "Name": "Test"}
    
    print("Running map_oracle_to_db with forced error...")
    result = map_oracle_to_db(item, db_mock)
    
    print(f"Result (should be None): {result}")
    
    # Check if rollback was called
    if db_mock.rollback.called:
        print("✅ SUCCESS: db.rollback() was called!")
    else:
        print("❌ FAILURE: db.rollback() was NOT called!")

if __name__ == "__main__":
    test_rollback_on_error()
