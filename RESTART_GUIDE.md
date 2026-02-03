# Frontend Restart Guide

## 🔄 Quick Restart

### Option 1: Use the Batch File (Easiest)
Double-click this file:
```
restart_frontend.bat
```
This will:
1. Stop any existing dev server
2. Start a new dev server
3. Open your browser to the Action Required dashboard
4. Remind you to hard refresh

### Option 2: Manual Restart

**Step 1: Stop the Current Server**
- Find the terminal/command prompt running the dev server
- Press `Ctrl + C` to stop it
- Wait for it to fully stop

**Step 2: Start the Server**
Open a new command prompt and run:
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\frontend"
npm run dev
```

**Step 3: Wait for Server to Start**
Look for a message like:
```
  ➜  Local:   http://localhost:5176/
  ➜  Network: use --host to expose
```

**Step 4: Open Browser**
Navigate to:
```
http://localhost:5176/practice-head/action-required
```

**Step 5: Hard Refresh**
Press `Ctrl + Shift + R` to clear cache and load new code

## ✅ What You Should See

After the hard refresh, you should see:

### Two Large Cards:

**Left Card (Blue)**
```
┌─────────────────────────────────┐
│ 1. Assign to Solution Architect │ (Blue header #1976D2)
├─────────────────────────────────┤
│ • Opportunity 1     [Assign]    │
│ • Opportunity 2     [Assign]    │
│ • Opportunity 3     [Assign]    │
└─────────────────────────────────┘
```

**Right Card (Red)**
```
┌─────────────────────────────────┐
│ 2. Review & Approve/Reject      │ (Red header #C62828)
├─────────────────────────────────┤
│ • Assessment 1    [✅] [❌] [🔗] │
│ • Assessment 2    [✅] [❌] [🔗] │
└─────────────────────────────────┘
```

## 🐛 Troubleshooting

### "Port 5176 is already in use"
```bash
# Kill the process using port 5176
netstat -ano | findstr :5176
# Note the PID (last column)
taskkill /F /PID <PID>
```

### "npm: command not found"
Make sure you're in the frontend directory:
```bash
cd frontend
```

### "Still seeing old dashboard"
1. **Hard refresh**: `Ctrl + Shift + R`
2. **Clear all cache**: 
   - Press F12
   - Right-click refresh button
   - Select "Empty Cache and Hard Reload"
3. **Close and reopen browser**

### "Two cards not showing"
Check the URL - it must be:
```
http://localhost:5176/practice-head/action-required
```
NOT:
- ❌ `http://localhost:5173/...` (wrong port)
- ❌ `http://localhost:5176/` (missing route)
- ❌ `http://localhost:5176/practice-head/review` (wrong route)

## 📊 Verification Steps

1. [ ] Dev server is running (check terminal)
2. [ ] URL is `http://localhost:5176/practice-head/action-required`
3. [ ] Hard refresh done (`Ctrl + Shift + R`)
4. [ ] See blue card on left
5. [ ] See red card on right
6. [ ] Blue card says "1. Assign to Solution Architect"
7. [ ] Red card says "2. Review & Approve/Reject"

## 🚀 Quick Commands

**Check if server is running:**
```bash
netstat -ano | findstr :5176
```

**Kill server:**
```bash
taskkill /F /PID <PID>
```

**Start server:**
```bash
cd frontend
npm run dev
```

**Open browser:**
```bash
start http://localhost:5176/practice-head/action-required
```

---

**Last Updated**: 2026-01-30
**Your Port**: 5176
**Target URL**: `http://localhost:5176/practice-head/action-required`
