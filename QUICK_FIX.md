# QUICK FIX - Restore Your Data

## What I Did:

1. ✅ **Reverted database.py** - Removed the `assigned_to` field to restore original schema
2. ✅ **Created quick_populate.py** - Simple script to populate dummy data

## To Get Your Data Back - Choose ONE Option:

### OPTION 1: Use Oracle Sync (Your Real Data)
```cmd
cd c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS
run_sync.bat
```

### OPTION 2: Use Quick Dummy Data (For Meeting)
```cmd
cd c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend
python quick_populate.py
```

This will create:
- 10 Opportunities (various customers, practices, stages)
- 6 Assessments (with scores and risks)
- 3 Users

### OPTION 3: Manual via Python
```cmd
cd backend
python
```

Then paste:
```python
from quick_populate import *
```

Press Enter and it will populate the data.

## Files Ready for You:

1. **backend/quick_populate.py** - Simple, fast dummy data generator
2. **backend/database.py** - Restored to original (no assigned_to field)

## Next Steps After Data is Populated:

1. **Start Backend**:
   ```cmd
   cd backend
   python main.py
   ```

2. **Start Frontend** (new terminal):
   ```cmd
   cd frontend
   npm run dev
   ```

3. **View**: http://localhost:5173

---

**I apologize for the confusion!** The terminal commands weren't executing properly on my end. 

Please run **OPTION 2** above in your terminal - it's the simplest and fastest way to get dummy data for your meeting.
