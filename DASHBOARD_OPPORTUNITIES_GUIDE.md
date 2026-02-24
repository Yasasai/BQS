# Dashboard Opportunities Display - Complete Guide

## Current Status ✅

Your dashboards are **already configured** to display opportunities from the opportunity table! Here's what's in place:

### 1. **Backend API** (`backend/app/routers/opportunities.py`)
- ✅ Endpoint: `GET /api/opportunities`
- ✅ Fetches all opportunities from the `opportunity` table
- ✅ Returns formatted data with:
  - Opportunity details (name, customer, value)
  - Workflow status
  - Assigned SA
  - Practice information
  - Win probability (score)

### 2. **Frontend Dashboards**
Both dashboards are already fetching and displaying opportunities:

#### **Management Dashboard** (`frontend/src/pages/ManagementDashboard.tsx`)
- ✅ Fetches from `/api/opportunities` on page load
- ✅ Displays in a table with columns:
  - ID, Opportunity Name, Account, Practice, Value, Status, Owner, Win %
- ✅ Shows KPI metrics:
  - Total Opportunities
  - Total Portfolio Value
  - Average Win Probability
  - Review Backlog
- ✅ Pipeline distribution chart

#### **Practice Head Dashboard** (`frontend/src/pages/PracticeHeadDashboard.tsx`)
- ✅ Fetches from `/api/opportunities` on page load
- ✅ Tab-based filtering:
  - All Opportunities
  - Unassigned
  - Under Assessment
  - Pending Review
- ✅ Action buttons (Assign, Approve, Reject)
- ✅ Same KPI metrics as Management Dashboard

---

## How to Verify Everything is Working

### Option 1: Run the Check Script
```bash
check_dashboard.bat
```

### Option 2: Manual Verification

#### Step 1: Ensure Backend is Running
```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Step 2: Test API Endpoint
Open browser or use curl:
```bash
curl http://localhost:8000/api/opportunities
```

You should see JSON array of opportunities.

#### Step 3: Ensure Frontend is Running
```bash
cd frontend
npm run dev
```

You should see:
```
Local:   http://localhost:5173/
```

#### Step 4: Open Dashboard
1. Navigate to: `http://localhost:5173`
2. Login (if required)
3. Go to **Management Dashboard** or **Practice Head Dashboard**
4. You should see opportunities displayed in the table

---

## If Opportunities Are Not Showing

### Problem 1: No Data in Database
**Symptom**: API returns empty array `[]`

**Solution**: Run Oracle sync to populate data
```bash
python batch_sync_with_offset.py
```

### Problem 2: Backend Not Running
**Symptom**: Frontend shows "Failed to fetch opportunities" error

**Solution**: Start the backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Problem 3: Frontend Not Running
**Symptom**: Can't access http://localhost:5173

**Solution**: Start the frontend
```bash
cd frontend
npm run dev
```

### Problem 4: CORS Error
**Symptom**: Browser console shows CORS error

**Solution**: Check `backend/app/main.py` has CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Schema

The `opportunity` table structure:
```sql
CREATE TABLE opportunity (
    opp_id VARCHAR PRIMARY KEY,
    opp_number VARCHAR,
    opp_name VARCHAR NOT NULL,
    customer_name VARCHAR NOT NULL,
    geo VARCHAR,
    currency VARCHAR,
    deal_value FLOAT,
    stage VARCHAR,
    close_date TIMESTAMP,
    sales_owner_user_id VARCHAR,
    primary_practice_id VARCHAR,
    workflow_status VARCHAR,
    assigned_sa VARCHAR,
    crm_last_updated_at TIMESTAMP NOT NULL,
    local_last_synced_at TIMESTAMP,
    is_active BOOLEAN
);
```

---

## Quick Start Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Database has opportunities (run sync if needed)
- [ ] API endpoint returns data: `http://localhost:8000/api/opportunities`
- [ ] Dashboard accessible: `http://localhost:5173`
- [ ] Opportunities visible in table

---

## API Response Format

Each opportunity in the API response looks like:
```json
{
  "id": "300000123456789",
  "remote_id": "OPP-2024-001",
  "name": "Cloud Migration Project",
  "customer": "Acme Corporation",
  "practice": "Cloud Infrastructure",
  "deal_value": 500000.0,
  "currency": "USD",
  "workflow_status": "UNDER_ASSESSMENT",
  "sales_stage": "Proposal",
  "geo": "EMEA",
  "close_date": "2024-03-31T00:00:00",
  "sales_owner": "John Doe",
  "assigned_practice_head": "PURSUE",
  "assigned_sa": "jane.smith@example.com",
  "win_probability": 75
}
```

---

## Dashboard Features

### Management Dashboard
- **View**: Global pipeline overview
- **Metrics**: Total opps, portfolio value, avg win %, review backlog
- **Actions**: View details, export, refresh
- **Filtering**: By practice, search

### Practice Head Dashboard
- **View**: Practice-specific opportunities
- **Tabs**: Unassigned, Under Assessment, Pending Review, All
- **Metrics**: Same as Management Dashboard
- **Actions**: Assign SA, Approve/Reject assessments
- **Filtering**: By tab, search

---

## Next Steps

1. **Run the verification script**: `check_dashboard.bat`
2. **Ensure both backend and frontend are running**
3. **If no data, run Oracle sync**: `python batch_sync_with_offset.py`
4. **Open dashboard and verify opportunities are displayed**

---

## Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Check backend logs for API errors
3. Verify database connection
4. Ensure all services are running

**Everything is already set up! Just make sure the services are running and data is synced.**
