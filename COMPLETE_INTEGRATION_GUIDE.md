# 🔗 Complete Integration: Oracle CRM → Backend → Frontend

## Overview
This document shows the complete data flow from Oracle CRM to your frontend application through the PostgreSQL backend.

---

## 🔄 **Complete Data Flow**

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Oracle CRM (Source)                                │
└─────────────────────────────────────────────────────────────┘
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
&q=RecordSet='ALL'

        ↓ (Sync Process)

┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Backend Sync (sync_manager.py)                     │
└─────────────────────────────────────────────────────────────┘
- Fetches data from Oracle API
- Maps Oracle fields to database columns
- Saves to PostgreSQL

        ↓ (Stored in Database)

┌─────────────────────────────────────────────────────────────┐
│  STEP 3: PostgreSQL Database                                │
└─────────────────────────────────────────────────────────────┘
Database: bqs
Table: opportunities
Columns: opp_id, opp_number, opp_name, customer_name, deal_value, etc.

        ↓ (API Endpoint)

┌─────────────────────────────────────────────────────────────┐
│  STEP 4: FastAPI Backend (main.py)                          │
└─────────────────────────────────────────────────────────────┘
GET http://localhost:8000/api/inbox/unassigned
Returns: JSON array of opportunities

        ↓ (Frontend Fetch)

┌─────────────────────────────────────────────────────────────┐
│  STEP 5: React Frontend (OpportunityInbox.tsx)              │
└─────────────────────────────────────────────────────────────┘
http://localhost:5173
Displays: Metrics cards + Data table
```

---

## 📊 **Data Mapping**

### **Oracle CRM → PostgreSQL**

| Oracle API Field | PostgreSQL Column | Frontend Display |
|------------------|-------------------|------------------|
| `OptyId` | `opp_id` | Hidden (used for routing) |
| `OptyNumber` | `opp_number` | Opportunity Nbr |
| `Name` | `opp_name` | Name (clickable link) |
| `TargetPartyName` | `customer_name` | Account |
| `Revenue` | `deal_value` | Amount ($2.7M) |
| `SalesStage` | `sales_stage` | Sales Stage |
| `Practice_c` | `practice` | Practice |
| `GEO_c` | `region` | Region |
| `Status` | `status` | Status (badge) |
| `EffectiveDate` | `creation_date` | Creation Date |
| `WinProb` | `win_probability` | Win (%) badge |

---

## 🚀 **Step-by-Step Integration**

### **STEP 1: Sync Oracle CRM to PostgreSQL**

#### **Option A: Auto-Sync on Backend Startup**

```bash
# Navigate to project
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"

# Start backend (auto-syncs on startup)
python -m backend.app.main
```

**What happens:**
```
🚀 BQS Starting...
🚀 Starting CLEAN Dynamic Sync...
📡 Fetching: Offset 0, Limit 50
   Processing 50 items...
   ✓ Saved: IAM one outsource 12m o...
   ✓ Saved: 1672704 STC-12 Months...
   ...
🎉 Sync Complete! Total Saved: 150 opportunities
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### **Option B: Manual Sync Before Starting Backend**

```bash
# Run sync manually
python -m backend.app.services.sync_manager

# Then start backend
python -m backend.app.main
```

#### **Option C: Force Sync via API**

```bash
# Start backend first
python -m backend.app.main

# In another terminal, trigger sync
curl -X POST http://localhost:8000/api/sync-force
```

---

### **STEP 2: Verify Data in PostgreSQL**

```bash
# Connect to database
psql -U postgres -d bqs

# Check data
SELECT COUNT(*) FROM opportunities;

# View sample
SELECT opp_id, opp_number, opp_name, customer_name, deal_value 
FROM opportunities 
LIMIT 5;

# Exit
\q
```

**Expected Output:**
```
 count 
-------
   150

 opp_id | opp_number | opp_name                    | customer_name              | deal_value 
--------+------------+-----------------------------+----------------------------+------------
 123456 | 1902737    | IAM one outsource 12m o...  | Beta Information Technology| 270005.00
 123457 | 1672704    | 1672704 STC-12 Months       | SAS Middle East FZ-LLC C   | 252000.00
 ...
```

---

### **STEP 3: Verify Backend API**

```bash
# Test API endpoint
curl http://localhost:8000/api/inbox/unassigned
```

**Expected Response:**
```json
[
  {
    "opp_id": "123456",
    "opp_number": "1902737",
    "opp_name": "IAM one outsource 12m o...",
    "customer_name": "Beta Information Technology",
    "deal_value": 270005.00,
    "sales_owner": "Kamal AL Al Safi",
    "practice": "IAM - Cybertech",
    "status": "Committed",
    "creation_date": "2024-01-23T00:00:00",
    "win_probability": 100,
    ...
  },
  ...
]
```

---

### **STEP 4: Start Frontend**

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not done)
npm install

# Start frontend
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

### **STEP 5: View in Browser**

```
http://localhost:5173
```

**You'll see:**

```
┌─────────────────────────────────────────────────────────────┐
│  Oracle Header (inspira + Great Place To Work)             │
├─────────────────────────────────────────────────────────────┤
│  Opportunities (?)                                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │ Total    │ Pipeline │ Avg Win  │ Pending  │            │
│  │ Opps: 150│ Value:$45M│ Prob: 68%│ Actions:45│           │
│  └──────────┴──────────┴──────────┴──────────┘            │
├─────────────────────────────────────────────────────────────┤
│  [Filters] Find[___] List[All▼]  [Refresh] [Actions▼]     │
├─────────────────────────────────────────────────────────────┤
│  Win% | Opp# | Name | Owner | Practice | Status | ...      │
│  100  |1902737| IAM...| Kamal | IAM     |Committed| ...    │
│  100  |1672704| STC...| Kamal | Analytics|Committed| ...   │
│  100  |1673697| IMR...| Afzal | Infra   |Committed| ...    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Verification Checklist**

### **1. Oracle CRM Connection**
```bash
# Test Oracle API directly
curl -u "yasasvi.upadrasta@inspiraenterprise.com:Welcome@123" \
"https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&q=RecordSet='ALL'&limit=5"
```
✅ Should return JSON with opportunities

### **2. PostgreSQL Database**
```bash
psql -U postgres -d bqs -c "SELECT COUNT(*) FROM opportunities;"
```
✅ Should return count > 0

### **3. Backend API**
```bash
curl http://localhost:8000/api/inbox/unassigned
```
✅ Should return JSON array

### **4. Frontend**
```
Open: http://localhost:5173
```
✅ Should show metrics and table with data

---

## 📝 **Complete Startup Sequence**

### **Terminal 1: Backend**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python -m backend.app.main
```

**Wait for:**
```
🎉 Sync Complete! Total Saved: 150 opportunities
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Terminal 2: Frontend**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\frontend"
npm run dev
```

**Wait for:**
```
➜  Local:   http://localhost:5173/
```

### **Browser:**
```
http://localhost:5173
```

---

## 🔄 **Data Refresh**

### **Auto-Refresh (On Backend Restart):**
```bash
# Stop backend (Ctrl+C)
# Start backend again
python -m backend.app.main
# Auto-syncs on startup
```

### **Manual Refresh (While Running):**
```bash
# Trigger sync via API
curl -X POST http://localhost:8000/api/sync-force
```

### **Frontend Refresh:**
```
# Click "Refresh" button in UI
# Or reload page (F5)
```

---

## 📊 **API Endpoints**

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/inbox/unassigned` | GET | Get all opportunities | JSON array |
| `/api/sync-force` | POST | Trigger manual sync | Status message |
| `/api/auth/users` | GET | Get users | User list |
| `/api/score/{id}` | GET | Get opportunity details | Opportunity object |

---

## 🎯 **Frontend Data Flow**

```typescript
// OpportunityInbox.tsx

useEffect(() => {
    fetchOpportunities();
}, []);

const fetchOpportunities = async () => {
    // 1. Fetch from backend API
    const response = await fetch('http://localhost:8000/api/inbox/unassigned');
    const data = await response.json();
    
    // 2. Set state
    setOpportunities(data);
    
    // 3. Calculate metrics
    const total = data.length;
    const totalValue = sum of deal_value;
    const avgWin = average of win_probability;
    
    // 4. Update UI
    setMetrics({ total, totalValue, avgWin, ... });
};
```

---

## 🔧 **Troubleshooting**

### **No Data in Frontend**

**Check 1: Backend Running?**
```bash
curl http://localhost:8000/api/inbox/unassigned
```
If error → Start backend

**Check 2: Data in Database?**
```bash
psql -U postgres -d bqs -c "SELECT COUNT(*) FROM opportunities;"
```
If 0 → Run sync

**Check 3: Sync Completed?**
```bash
# Check backend logs for:
🎉 Sync Complete! Total Saved: X opportunities
```
If not → Run sync manually

**Check 4: CORS Error?**
```
Check browser console for CORS errors
```
Backend has CORS enabled for all origins

---

### **Sync Fails**

**Error: "401 Unauthorized"**
```
Check .env file:
- ORACLE_USER correct?
- ORACLE_PASSWORD correct?
- No extra spaces?
```

**Error: "Connection refused"**
```
Check PostgreSQL:
- Is it running?
- Can you connect with psql?
```

**Error: "0 records"**
```
Check Oracle API:
- Test in Postman
- Verify q parameter
- Check user permissions
```

---

## 📋 **Environment Variables**

### **Required in `.env`:**

```env
# Oracle CRM
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com
ORACLE_PASSWORD=Welcome@123
ORACLE_API_VERSION=11.12.1.0

# PostgreSQL
DATABASE_URL=postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs
```

✅ **Your .env is correct!**

---

## 🎉 **Success Indicators**

### **1. Backend Logs:**
```
🚀 BQS Starting...
🚀 Starting CLEAN Dynamic Sync...
📡 Fetching: Offset 0, Limit 50
   ✓ Saved: Opportunity 1
   ✓ Saved: Opportunity 2
   ...
🎉 Sync Complete! Total Saved: 150 opportunities
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **2. Database:**
```sql
SELECT COUNT(*) FROM opportunities;
-- Returns: 150
```

### **3. API Response:**
```bash
curl http://localhost:8000/api/inbox/unassigned
-- Returns: JSON array with 150 items
```

### **4. Frontend:**
```
Metrics show:
- Total Opportunities: 150
- Pipeline Value: $45.2M
- Table shows all 150 opportunities
```

---

## 🎯 **Summary**

### **Complete Integration Path:**

```
Oracle CRM
    ↓ (API Call)
Backend Sync (sync_manager.py)
    ↓ (Save)
PostgreSQL Database
    ↓ (Query)
FastAPI Backend (main.py)
    ↓ (HTTP Request)
React Frontend (OpportunityInbox.tsx)
    ↓ (Display)
Browser (localhost:5173)
```

### **To Start Everything:**

1. **Start Backend:**
   ```bash
   python -m backend.app.main
   ```
   (Auto-syncs from Oracle)

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser:**
   ```
   http://localhost:5173
   ```

4. **See Your Oracle Data!**

---

**Your Oracle CRM is now fully integrated with your frontend application!** 🎉
