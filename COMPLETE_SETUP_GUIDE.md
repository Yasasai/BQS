# 🚀 Complete Setup Guide - Action Required Dashboard

## The Solution

You need to run **BOTH** frontend AND backend at the same time!

The Action Required dashboard is working, but it's empty because:
1. The backend API isn't running (or)
2. The `workflow_status` field in database is empty

## 📋 Quick Start (3 Steps)

### Step 1: Start Both Servers
**Double-click this file:**
```
start_both_servers.bat
```

This will open **TWO terminal windows**:
- 🐍 **Backend API** (Python/FastAPI) on port 8000
- ⚛️ **Frontend** (Vite/React) on port 5176

**Wait** until you see:
- Backend: "Application startup complete"
- Frontend: "Local: http://localhost:5176/"

### Step 2: Populate Database
**Double-click this file:**
```
run_sync_script.bat
```

This populates the `workflow_status` field for all opportunities.

**Wait** for it to say "Sync Complete!"

### Step 3: View Dashboard
Your browser should open automatically to:
```
http://localhost:5176/practice-head/action-required
```

**Press: Ctrl + Shift + R** (hard refresh)

You should now see opportunities in the two colored cards!

---

## 🎯 What You'll See

### Left Card (Oracle Blue #1976D2)
**"1. Assign to Solution Architect"**
- Shows opportunities where `assigned_sa` is NULL or "Unassigned"
- Each has a blue "Assign" button

### Right Card (Oracle Red #C62828)
**"2. Review & Approve/Reject"**
- Shows opportunities where `workflow_status` = "SUBMITTED_FOR_REVIEW"
- Each has ✅ ❌ 🔗 buttons

---

## ❓ Troubleshooting

### "Still no opportunities showing"

**Check 1: Are both servers running?**
You should have TWO terminal windows open:
- Backend (port 8000)
- Frontend (port 5176)

**Check 2: Did you run the sync script?**
Run `run_sync_script.bat` to populate workflow_status

**Check 3: Do opportunities exist in database?**
Open: `http://localhost:8000/api/opportunities`
Should show JSON with opportunities

**Check 4: Check workflow_status values**
Look at the JSON from Step 3 - each opportunity should have:
```json
{
  "id": 123,
  "name": "Some Opportunity",
  "workflow_status": "NEW",  // ← This field must exist!
  "assigned_sa": null
}
```

### "Backend won't start"

**Error: "Address already in use"**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /F /PID <PID>
```

**Error: "No module named 'uvicorn'"**
```bash
cd backend
pip install -r requirements.txt
```

### "Frontend won't start"

**Error: "Port 5176 already in use"**
```bash
# Kill process on port 5176
netstat -ano | findstr :5176
# Note the PID, then:
taskkill /F /PID <PID>
```

**Error: "npm: command not found"**
```bash
cd frontend
npm install
```

---

## 🔄 Daily Workflow

### Starting Your Day
1. Double-click: `start_both_servers.bat`
2. Wait for both to start
3. Open browser to: `http://localhost:5176/practice-head/action-required`

### Ending Your Day
Close both terminal windows (Backend and Frontend)

### If Opportunities Don't Update
Run: `run_sync_script.bat`
This syncs the latest data from Oracle CRM

---

## 📊 Understanding the Data Flow

```
Oracle CRM
    ↓
Backend Sync (sync_workflow_status.py)
    ↓
PostgreSQL Database (workflow_status populated)
    ↓
Backend API (port 8000)
    ↓
Frontend (port 5176)
    ↓
Action Required Dashboard
```

All parts must be working for opportunities to show!

---

## ✅ Verification Checklist

- [ ] Backend running (check terminal window)
- [ ] Frontend running (check terminal window)
- [ ] Sync script executed successfully
- [ ] Browser at correct URL: `http://localhost:5176/practice-head/action-required`
- [ ] Hard refresh done (Ctrl+Shift+R)
- [ ] Two colored cards visible (blue and red)
- [ ] Opportunities showing in cards

---

## 🎉 Success!

When everything is working:
- ✅ Two terminal windows open (backend + frontend)
- ✅ Browser shows two colored cards
- ✅ Opportunities listed in the cards
- ✅ Can click "Assign" button
- ✅ Can click ✅ ❌ 🔗 buttons

---

**Files Created**:
- `start_both_servers.bat` - Starts both servers
- `run_sync_script.bat` - Populates workflow_status
- This guide - Complete instructions

**Last Updated**: 2026-01-30 09:42 IST
