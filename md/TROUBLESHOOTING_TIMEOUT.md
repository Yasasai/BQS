# 🔧 Troubleshooting: Backend Timeout Issue

## ❌ Error You're Seeing

```
✗ ERROR: HTTPConnectionPool(host='localhost', port=8000): Read timed out. (read timeout=5)
```

## 🔍 What This Means

The backend is running, but it's taking longer than 5 seconds to respond. This is **normal** for the first request because:

1. **Database initialization** - Creating tables, checking schema
2. **Oracle CRM connection** - First connection can be slow
3. **Network latency** - VPN or network delays
4. **Heavy processing** - If sync is already running

## ✅ Solutions

### **Solution 1: Use Updated Script (Recommended)**

I've updated `trigger_sync.py` with a **30-second timeout**. Run it again:

```bash
python trigger_sync.py
```

Or double-click: `SYNC_NOW.bat`

---

### **Solution 2: Use Simple Health Check**

Run this to verify backend and trigger sync:

```bash
python check_backend.py
```

This has better timeout handling and diagnostics.

---

### **Solution 3: Use Browser (Most Reliable)**

1. Open browser: http://localhost:8000/docs
2. Find **POST /api/sync-database**
3. Click "Try it out"
4. Click "Execute"

This won't timeout and you can see the response directly.

---

### **Solution 4: Check Backend Console**

Look at your backend console (where you ran `python main.py`).

**If you see:**
```
INFO:     127.0.0.1:XXXXX - "POST /api/sync-database HTTP/1.1" 200 OK
```

Then the sync **IS working**, even if the script timed out!

---

## 📊 Monitor Sync Progress

### **Option 1: Backend Console**
Watch your backend console for output like:
```
============================================================
🔄 FULL SYNC - First time synchronization
============================================================
📡 Fetching opportunities from Oracle CRM...
Fetching batch: offset=0, limit=500
✓ Fetched 150 opportunities (Total: 150)
✓ Fetched 150 total opportunities from Oracle.
💾 Syncing to PostgreSQL...
[1/150] Processing...
✓ Created: Opportunity Name (ID: 12345)
...
```

### **Option 2: Browser**
Visit: http://localhost:8000/api/sync-status

### **Option 3: API Docs**
Visit: http://localhost:8000/docs
- Find GET /api/sync-status
- Click "Try it out"
- Click "Execute"

---

## 🎯 Quick Diagnosis

Run this in PowerShell to check everything:

```powershell
# Check if backend is running
Invoke-RestMethod -Uri "http://localhost:8000/" -TimeoutSec 30

# Trigger sync
Invoke-RestMethod -Uri "http://localhost:8000/api/sync-database" -Method POST -TimeoutSec 30

# Check status
Invoke-RestMethod -Uri "http://localhost:8000/api/sync-status" -TimeoutSec 30
```

---

## 🔍 Common Causes & Fixes

### **1. Backend is Busy**
**Symptom:** Timeout on first request  
**Fix:** Wait a few seconds and try again

### **2. Oracle CRM is Slow**
**Symptom:** Long delays, eventual timeout  
**Fix:** 
- Check VPN connection
- Check Oracle CRM is accessible
- Use browser method (won't timeout)

### **3. Database is Initializing**
**Symptom:** First request times out  
**Fix:** Wait 10 seconds after starting backend, then try again

### **4. Sync Already Running**
**Symptom:** Backend doesn't respond  
**Fix:** Wait for current sync to complete (check backend console)

---

## ✅ Verification Steps

### **Step 1: Verify Backend is Running**
```bash
python check_backend.py
```

Expected output:
```
✓ Backend is responding!
✓ Sync endpoint responded with status: 200
✅ Backend is healthy and sync has been triggered!
```

### **Step 2: Check Sync Status**
Visit: http://localhost:8000/api/sync-status

Expected response:
```json
{
  "sync_type": "FULL",
  "status": "SUCCESS",
  "total_fetched": 150,
  "new_records": 150,
  ...
}
```

### **Step 3: Verify Data**
Visit: http://localhost:8000/api/opportunities

You should see a JSON array of opportunities.

---

## 🚀 Recommended Workflow

**For Immediate Sync:**

1. **Open browser** → http://localhost:8000/docs
2. **Find** POST /api/sync-database
3. **Click** "Try it out" → "Execute"
4. **Watch** backend console for progress
5. **Check** http://localhost:8000/api/sync-status when done

**This method never times out and gives you full control!**

---

## 📝 What's Happening Behind the Scenes

When you trigger a sync:

1. **API receives request** (instant)
2. **Sync starts in background** (instant)
3. **API returns success** (instant)
4. **Sync runs independently** (takes time)

The timeout happens because the script waits for the API response, but if the backend is busy initializing, it delays the response.

**Solution:** The sync is likely running even if you get a timeout!

---

## 🎯 Next Steps

1. **Try the updated script:** `python trigger_sync.py`
2. **Or use browser method:** http://localhost:8000/docs
3. **Watch backend console** for sync progress
4. **Check status when done:** http://localhost:8000/api/sync-status

---

## ✅ Summary

**The Issue:** 5-second timeout was too short  
**The Fix:** Updated to 30-second timeout  
**Best Method:** Use browser (http://localhost:8000/docs)  
**Monitoring:** Watch backend console or check /api/sync-status  

**Your backend IS running - just use the browser method for most reliable results!** 🚀
