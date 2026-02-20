# 🔄 Oracle CRM to PostgreSQL Sync - Quick Start Guide

## Problem
Your Oracle CRM data is not yet synced to PostgreSQL database. You need to run the sync to populate the database.

---

## ✅ **Quick Sync Steps**

### **Option 1: Run Sync Script (Recommended)**

```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python -m backend.app.services.sync_manager
```

**What it does:**
- Connects to Oracle CRM
- Fetches all opportunities
- Saves them to PostgreSQL
- Shows progress in terminal

**Expected Output:**
```
🚀 Starting CLEAN Dynamic Sync...
📡 Fetching: Offset 0, Limit 50
   Processing 50 items...
   ✓ Saved: IAM one outsource 12m o...
   ✓ Saved: 1672704 STC-12 Months...
   ✓ Saved: 1673697 revised IMR DDo...
   ...
📡 Fetching: Offset 50, Limit 50
   Processing 50 items...
   ...
✅ No more items found.
🎉 Sync Complete! Total Saved: 150 opportunities
```

---

### **Option 2: Run via Python Directly**

```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python backend/app/services/sync_manager.py
```

---

### **Option 3: Run via Backend API**

1. **Start the backend:**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python -m backend.app.main
```

2. **In another terminal, trigger sync:**
```bash
curl http://localhost:8000/api/sync/opportunities
```

---

## 🔍 **Verify Sync Worked**

### **Check Database:**

```bash
# Connect to PostgreSQL
psql -U postgres -d bqs

# Count opportunities
SELECT COUNT(*) FROM opportunities;

# View sample data
SELECT opp_id, opp_number, opp_name, customer_name, deal_value 
FROM opportunities 
LIMIT 10;

# Exit
\q
```

**Expected Result:**
```
 count 
-------
   150
(1 row)
```

---

### **Check via API:**

```bash
# Get all opportunities
curl http://localhost:8000/api/inbox/unassigned

# Should return JSON array with opportunities
```

---

## 📋 **Prerequisites Check**

### **1. Check .env File**

File: `c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\.env`

**Required variables:**
```env
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com
ORACLE_PASSWORD=Welcome@123
DATABASE_URL=postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs
ORACLE_API_VERSION=11.12.1.0
```

✅ **Your .env is correct!**

---

### **2. Check PostgreSQL is Running**

```bash
# Test connection
psql -U postgres -d bqs -c "SELECT 1;"
```

**Expected:**
```
 ?column? 
----------
        1
(1 row)
```

---

### **3. Check Python Dependencies**

```bash
pip list | findstr httpx
pip list | findstr sqlalchemy
pip list | findstr psycopg2
```

**Expected:**
```
httpx                  0.x.x
sqlalchemy             2.x.x
psycopg2-binary        2.x.x
```

---

## 🚀 **Step-by-Step Execution**

### **Step 1: Open Terminal**
- Press `Win + R`
- Type `cmd`
- Press Enter

### **Step 2: Navigate to Project**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
```

### **Step 3: Run Sync**
```bash
python -m backend.app.services.sync_manager
```

### **Step 4: Watch Progress**
You'll see:
```
🚀 Starting CLEAN Dynamic Sync...
📡 Fetching: Offset 0, Limit 50
   Processing 50 items...
   ✓ Saved: Opportunity 1
   ✓ Saved: Opportunity 2
   ...
```

### **Step 5: Wait for Completion**
```
🎉 Sync Complete! Total Saved: 150 opportunities
```

### **Step 6: Verify**
```bash
# Check database
psql -U postgres -d bqs -c "SELECT COUNT(*) FROM opportunities;"
```

---

## ⚠️ **Troubleshooting**

### **Error: "No module named 'backend'"**

**Solution:**
```bash
# Make sure you're in the project root
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"

# Run with -m flag
python -m backend.app.services.sync_manager
```

---

### **Error: "Connection refused" (PostgreSQL)**

**Solution:**
```bash
# Start PostgreSQL service
net start postgresql-x64-14

# Or check if running
pg_ctl status
```

---

### **Error: "401 Unauthorized" (Oracle)**

**Solution:**
Check your `.env` file:
- `ORACLE_USER` is correct
- `ORACLE_PASSWORD` is correct
- No extra spaces in credentials

---

### **Error: "0 records" or "No items found"**

**Solution:**
This is expected if:
- Oracle has no opportunities
- Your user has no access

**Check in Postman:**
```
GET https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
&q=RecordSet='ALL'
&limit=10

Auth: Basic (your credentials)
```

---

## 📊 **What Gets Synced**

### **Data Mapping:**

| Oracle Field | PostgreSQL Column | Description |
|--------------|-------------------|-------------|
| `OptyId` | `opp_id` | Opportunity ID |
| `OptyNumber` | `opp_number` | Opportunity Number |
| `Name` | `opp_name` | Opportunity Name |
| `TargetPartyName` | `customer_name` | Customer Name |
| `Revenue` | `deal_value` | Deal Value |
| `SalesStage` | `stage` | Sales Stage |
| `Practice_c` | `primary_practice_id` | Practice (via lookup) |
| `GEO_c` | `geo` | Geographic Region |
| `CurrencyCode` | `currency` | Currency |
| `EffectiveDate` | `close_date` | Close Date |
| `LastUpdateDate` | `crm_last_updated_at` | Last Updated |

---

## 🔄 **Sync Frequency**

### **Manual Sync:**
Run the command whenever you want to update data:
```bash
python -m backend.app.services.sync_manager
```

### **Automatic Sync (Future):**
The backend can be configured to sync automatically:
- Every 24 hours
- On application startup
- Via scheduled task

---

## ✅ **Success Indicators**

### **1. Terminal Output:**
```
🎉 Sync Complete! Total Saved: 150 opportunities
```

### **2. Database Check:**
```sql
SELECT COUNT(*) FROM opportunities;
-- Should return > 0
```

### **3. API Check:**
```bash
curl http://localhost:8000/api/inbox/unassigned
-- Should return JSON array
```

### **4. Frontend Check:**
```
http://localhost:5173
-- Should show opportunities in table
```

---

## 🎯 **Quick Command Reference**

```bash
# Navigate to project
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"

# Run sync
python -m backend.app.services.sync_manager

# Check database
psql -U postgres -d bqs -c "SELECT COUNT(*) FROM opportunities;"

# Start backend
python -m backend.app.main

# Start frontend
cd frontend
npm run dev
```

---

## 📝 **Next Steps After Sync**

1. **Verify Data:**
   ```bash
   psql -U postgres -d bqs -c "SELECT * FROM opportunities LIMIT 5;"
   ```

2. **Start Backend:**
   ```bash
   python -m backend.app.main
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Open Browser:**
   ```
   http://localhost:5173
   ```

5. **See Your Data:**
   - Main dashboard shows metrics
   - Table shows all opportunities
   - Click any row to see details

---

## 🎉 **Summary**

**To sync Oracle CRM to PostgreSQL:**

1. Open terminal
2. Navigate to project folder
3. Run: `python -m backend.app.services.sync_manager`
4. Wait for completion
5. Verify in database
6. Start backend and frontend
7. See data in browser!

**Your Oracle CRM will now be linked to PostgreSQL!** ✅
