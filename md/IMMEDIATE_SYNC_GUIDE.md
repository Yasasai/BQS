# 🔄 Immediate Sync Guide

## ✅ Backend is Running!

Your backend is successfully running with:
- ✅ Database initialized
- ✅ Schema up to date
- ✅ **Daily scheduler active** (syncs at midnight 00:00)

---

## 🚀 Trigger Immediate Sync (Backup Now)

You have **3 options** to trigger an immediate sync:

### **Option 1: Python Script (Recommended)**
```bash
python trigger_sync.py
```

This will:
1. Check if backend is running
2. Trigger the sync
3. Show sync status
4. Display progress

---

### **Option 2: Direct API Call (PowerShell)**
Open a **new terminal** and run:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/sync-database" -Method POST
```

---

### **Option 3: Browser**
Open your browser and visit:
```
http://localhost:8000/docs
```

Then:
1. Find the **POST /api/sync-database** endpoint
2. Click "Try it out"
3. Click "Execute"

---

## 📊 Check Sync Status

### **Option 1: API Call**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/sync-status" -Method GET
```

### **Option 2: Browser**
Visit: http://localhost:8000/api/sync-status

### **Option 3: Backend Console**
Watch your backend console (where you ran `python main.py`) for detailed logs:
```
============================================================
🔄 FULL SYNC - First time synchronization
============================================================
📡 Fetching opportunities from Oracle CRM...
✓ Fetched 150 opportunities from Oracle
💾 Syncing to PostgreSQL...
[1/150] Processing...
✓ Created: Opportunity Name (ID: 12345)
...
```

---

## 📅 Scheduled Sync

Your system is configured to automatically sync:
- **Frequency:** Daily
- **Time:** Midnight (00:00)
- **Type:** 
  - First sync: **FULL** (all opportunities)
  - Subsequent: **INCREMENTAL** (updates only)

**No manual intervention needed!** The sync will run automatically every day.

---

## 🔍 Verify Sync Completed

### Check Opportunities in Database
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/opportunities" -Method GET
```

Or visit: http://localhost:8000/api/opportunities

---

## 📊 Expected Sync Flow

```
1. Trigger sync (manual or scheduled)
   ↓
2. Backend fetches from Oracle CRM
   ↓
3. Data synced to PostgreSQL
   ↓
4. Sync status logged to database
   ↓
5. Frontend can now access data
```

---

## ⏰ Current Schedule

**Automatic Sync:**
- **Next sync:** Tonight at 00:00 (midnight)
- **Frequency:** Every 24 hours
- **Type:** Incremental (updates existing records)

**Manual Sync:**
- **Anytime:** Run `python trigger_sync.py`
- **Type:** Full or Incremental (auto-detected)

---

## ✅ Summary

**Right Now:**
1. ✅ Backend is running
2. ✅ Scheduler is active (daily at midnight)
3. 🔄 **Run `python trigger_sync.py` for immediate backup**

**Going Forward:**
- ✅ Automatic daily sync at midnight
- ✅ Manual sync anytime via `trigger_sync.py`
- ✅ Monitor via `/api/sync-status`

---

## 🎯 Quick Commands

```bash
# Trigger immediate sync
python trigger_sync.py

# Check sync status
python -c "import requests; print(requests.get('http://localhost:8000/api/sync-status').json())"

# View opportunities
python -c "import requests; print(f'Total opportunities: {len(requests.get(\"http://localhost:8000/api/opportunities\").json())}')"
```

---

**Your system is ready! Run `python trigger_sync.py` now for your immediate backup.** 🚀
