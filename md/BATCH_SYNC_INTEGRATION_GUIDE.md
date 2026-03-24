# 🔗 Batch Sync Integration - Complete Guide

## Overview
The batch sync with offset tracking is now **fully integrated** into the FastAPI backend as a new router with API endpoints.

---

## ✅ **What Was Integrated**

### **1. New Router Created**
**File:** `backend/app/routers/batch_sync.py`

**Provides 6 API endpoints:**
- `POST /api/batch-sync/start` - Start batch sync (background)
- `POST /api/batch-sync/start-sync` - Start batch sync (synchronous)
- `GET /api/batch-sync/status` - Get sync status
- `POST /api/batch-sync/reset` - Reset sync state
- `GET /api/batch-sync/count` - Get synced count
- `GET /api/batch-sync/health` - Health check

### **2. Main App Updated**
**File:** `backend/app/main.py`

**Changes:**
```python
# Added import
from backend.app.routers import auth, inbox, scoring, batch_sync

# Added router
app.include_router(batch_sync.router)  # ← NEW
```

---

## 🚀 **How to Use**

### **Step 1: Start Backend**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python -m backend.app.main
```

**Expected:**
```
🚀 BQS Starting...
...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 2: Use API Endpoints**

---

## 📋 **API Endpoints**

### **1. Start Batch Sync (Background)**

```bash
curl -X POST "http://localhost:8000/api/batch-sync/start" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 5, "sync_name": "oracle_opportunities"}'
```

**Response:**
```json
{
  "status": "started",
  "message": "Batch sync started with batch_size=5",
  "batch_size": 5,
  "sync_name": "oracle_opportunities"
}
```

**What it does:**
- Starts sync in background
- Returns immediately
- Sync continues running

---

### **2. Start Batch Sync (Synchronous)**

```bash
curl -X POST "http://localhost:8000/api/batch-sync/start-sync?batch_size=5"
```

**Response:**
```json
{
  "status": "complete",
  "message": "Batch sync completed successfully",
  "total_synced": 150,
  "batch_size": 5
}
```

**What it does:**
- Starts sync
- Waits for completion
- Returns total synced

---

### **3. Get Sync Status**

```bash
curl "http://localhost:8000/api/batch-sync/status?sync_name=oracle_opportunities"
```

**Response:**
```json
{
  "status": "success",
  "sync_name": "oracle_opportunities",
  "current_offset": 75,
  "total_synced": 75,
  "last_sync_at": "2024-01-16 13:24:00",
  "is_complete": false,
  "total_in_db": 75
}
```

**What it shows:**
- Current offset position
- Total records synced
- Last sync timestamp
- Completion status
- Total in database

---

### **4. Reset Sync**

```bash
curl -X POST "http://localhost:8000/api/batch-sync/reset?sync_name=oracle_opportunities"
```

**Response:**
```json
{
  "status": "success",
  "message": "Sync state reset for 'oracle_opportunities'",
  "sync_name": "oracle_opportunities"
}
```

**What it does:**
- Resets offset to 0
- Clears sync state
- Next sync starts from beginning

---

### **5. Get Synced Count**

```bash
curl "http://localhost:8000/api/batch-sync/count"
```

**Response:**
```json
{
  "status": "success",
  "count": 150,
  "table": "minimal_opportunities"
}
```

**What it shows:**
- Total records in `minimal_opportunities` table

---

### **6. Health Check**

```bash
curl "http://localhost:8000/api/batch-sync/health"
```

**Response:**
```json
{
  "status": "healthy",
  "module": "batch_sync_with_offset",
  "endpoints": [
    "POST /api/batch-sync/start",
    "POST /api/batch-sync/start-sync",
    "GET /api/batch-sync/status",
    "POST /api/batch-sync/reset",
    "GET /api/batch-sync/count",
    "GET /api/batch-sync/health"
  ]
}
```

---

## 🌐 **Swagger UI (Interactive Docs)**

### **Access:**
```
http://localhost:8000/docs
```

**You'll see:**
- All batch sync endpoints
- Try them out interactively
- See request/response schemas

**Navigate to:**
- Batch Sync section
- Click any endpoint
- Click "Try it out"
- Execute

---

## 📊 **Complete Workflow**

### **Scenario 1: Start Fresh Sync**

```bash
# 1. Reset (optional, if restarting)
curl -X POST "http://localhost:8000/api/batch-sync/reset"

# 2. Start sync
curl -X POST "http://localhost:8000/api/batch-sync/start" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 10}'

# 3. Check status
curl "http://localhost:8000/api/batch-sync/status"

# 4. Get count
curl "http://localhost:8000/api/batch-sync/count"
```

---

### **Scenario 2: Resume Interrupted Sync**

```bash
# 1. Check current status
curl "http://localhost:8000/api/batch-sync/status"
# Shows: offset=50, total_synced=50

# 2. Resume sync (automatically picks up from offset 50)
curl -X POST "http://localhost:8000/api/batch-sync/start" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 10}'

# 3. Check status again
curl "http://localhost:8000/api/batch-sync/status"
# Shows: offset=150, total_synced=150, is_complete=true
```

---

### **Scenario 3: Monitor Progress**

```bash
# Start sync
curl -X POST "http://localhost:8000/api/batch-sync/start" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 5}'

# Check status every few seconds
while true; do
  curl "http://localhost:8000/api/batch-sync/status"
  sleep 5
done
```

---

## 🔄 **Integration with Frontend**

### **React Component Example:**

```typescript
// Batch Sync Component
const BatchSyncControl: React.FC = () => {
    const [status, setStatus] = useState<any>(null);
    
    const startSync = async () => {
        const response = await fetch('http://localhost:8000/api/batch-sync/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_size: 10 })
        });
        const data = await response.json();
        console.log('Sync started:', data);
    };
    
    const checkStatus = async () => {
        const response = await fetch('http://localhost:8000/api/batch-sync/status');
        const data = await response.json();
        setStatus(data);
    };
    
    return (
        <div>
            <button onClick={startSync}>Start Batch Sync</button>
            <button onClick={checkStatus}>Check Status</button>
            
            {status && (
                <div>
                    <p>Offset: {status.current_offset}</p>
                    <p>Synced: {status.total_synced}</p>
                    <p>Complete: {status.is_complete ? 'Yes' : 'No'}</p>
                </div>
            )}
        </div>
    );
};
```

---

## 📁 **File Structure**

```
BQS/
├── batch_sync_with_offset.py          ← Core sync logic
├── backend/
│   └── app/
│       ├── main.py                     ← Updated (includes router)
│       └── routers/
│           ├── auth.py
│           ├── inbox.py
│           ├── scoring.py
│           └── batch_sync.py           ← NEW (API endpoints)
```

---

## 🔍 **Verify Integration**

### **1. Check Backend Logs**

Start backend and look for:
```
🚀 BQS Starting...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **2. Test Health Endpoint**

```bash
curl "http://localhost:8000/api/batch-sync/health"
```

Should return:
```json
{"status": "healthy", "module": "batch_sync_with_offset", ...}
```

### **3. Check Swagger Docs**

Visit: `http://localhost:8000/docs`

Look for "Batch Sync" section with 6 endpoints

---

## 📊 **Comparison: Standalone vs Integrated**

| Feature | Standalone | Integrated (API) |
|---------|-----------|------------------|
| **Run Method** | `python batch_sync_with_offset.py` | HTTP API calls |
| **Access** | Command line only | API, Frontend, Postman |
| **Background** | No | Yes (with `/start`) |
| **Status Check** | Command line | HTTP GET request |
| **Integration** | Separate script | Part of backend |
| **Use Case** | Testing, manual | Production, automated |

---

## ✅ **Summary**

### **What Was Done:**

1. ✅ Created `backend/app/routers/batch_sync.py`
   - 6 API endpoints
   - Background task support
   - Status monitoring

2. ✅ Updated `backend/app/main.py`
   - Imported batch_sync router
   - Included in app

3. ✅ Integration complete
   - Accessible via HTTP API
   - Works with frontend
   - Swagger docs available

### **How to Use:**

**Start Backend:**
```bash
python -m backend.app.main
```

**Use API:**
```bash
# Start sync
curl -X POST "http://localhost:8000/api/batch-sync/start" \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 10}'

# Check status
curl "http://localhost:8000/api/batch-sync/status"
```

**Or use Swagger UI:**
```
http://localhost:8000/docs
```

---

## 🎯 **Next Steps**

1. **Start Backend:**
   ```bash
   python -m backend.app.main
   ```

2. **Test Endpoints:**
   - Visit `http://localhost:8000/docs`
   - Try batch sync endpoints

3. **Integrate with Frontend:**
   - Add batch sync controls
   - Show sync progress
   - Display status

---

**Your batch sync is now fully integrated into the backend!** 🎉
