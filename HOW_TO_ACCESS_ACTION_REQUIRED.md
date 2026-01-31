# How to Access the Action Required Dashboard

## 🚀 Quick Access Guide

Your frontend is running on port **5176** (not 5173).

### Step 1: Navigate to the Dashboard

Open your browser and go to one of these URLs:

**Option 1: Direct URL (Recommended)**
```
http://localhost:5176/practice-head/action-required
```

**Option 2: Via Sidebar Menu**
1. Go to: `http://localhost:5176/`
2. Click the hamburger menu (☰) in the top-left corner
3. Look for "⚡ Action Required" under the "Practice Head" section
4. Click it

**Option 3: Any Practice Head Route**
```
http://localhost:5176/practice-head/unassigned
http://localhost:5176/practice-head/review
http://localhost:5176/practice-head/assign
```
Then click the hamburger menu and select "⚡ Action Required"

## 🔍 What You Should See

Once you navigate to the correct URL, you should see:

### Two Large Cards Side-by-Side:

**Left Card (Oracle Blue #1976D2)**
- Header: "1. Assign to Solution Architect"
- Shows unassigned opportunities
- Each has an "Assign" button

**Right Card (Oracle Red #C62828)**
- Header: "2. Review & Approve/Reject"
- Shows submitted assessments
- Each has ✅ ❌ 🔗 action buttons

## ❌ Troubleshooting

### "Page Not Found" or "Nothing Shows"

**Problem**: You're on the wrong URL
**Solution**: Make sure you're using port **5176** (not 5173)
```
✅ Correct: http://localhost:5176/practice-head/action-required
❌ Wrong:   http://localhost:5173/practice-head/action-required
```

### "I see the old dashboard"

**Problem**: Browser cache or dev server not reloaded
**Solution**: 
1. Hard refresh: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Or clear browser cache
3. Check if the dev server is running

### "The sidebar doesn't have Action Required"

**Problem**: Old code is still running
**Solution**:
1. Stop the frontend dev server (Ctrl+C in the terminal)
2. Restart it:
   ```bash
   cd frontend
   npm run dev
   ```
3. Wait for it to compile
4. Hard refresh your browser

### "I only see one tab/view"

**Problem**: You're looking at a different dashboard
**Solution**: Make sure you're on the Practice Head Dashboard, not:
- Management Dashboard (`/management/dashboard`)
- Solution Architect Dashboard (`/sa/assigned`)
- Opportunity Inbox (`/`)

## 📋 Verification Checklist

- [ ] Frontend is running on port 5176
- [ ] You're navigating to `http://localhost:5176/practice-head/action-required`
- [ ] You've done a hard refresh (Ctrl+Shift+R)
- [ ] You see two cards: one blue, one red
- [ ] The blue card says "1. Assign to Solution Architect"
- [ ] The red card says "2. Review & Approve/Reject"

## 🔄 If Still Not Working

1. **Check the dev server terminal** - Look for any errors
2. **Check browser console** (F12) - Look for JavaScript errors
3. **Verify the file was saved**:
   ```bash
   # Check if changes are in the file
   type frontend\src\pages\PracticeHeadDashboard.tsx | findstr "action-required"
   ```
4. **Restart everything**:
   ```bash
   # Stop the dev server (Ctrl+C)
   # Then restart:
   cd frontend
   npm run dev
   ```

## 📞 Quick Test

Open this URL in your browser:
```
http://localhost:5176/practice-head/action-required
```

If you see two colored cards (blue and red), it's working! ✅

If you see anything else, let me know what you see and I'll help troubleshoot.

---

**Your Port**: 5176
**Correct URL**: `http://localhost:5176/practice-head/action-required`
**Last Updated**: 2026-01-30
