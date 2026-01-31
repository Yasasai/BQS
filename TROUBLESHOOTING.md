# Troubleshooting: Opportunities Not Loading

## Quick Checks

### 1. Is the Backend Running?
Open a browser and go to: `http://127.0.0.1:8000/docs`
- ✅ If you see the FastAPI docs page → Backend is running
- ❌ If you get "can't connect" → Backend is NOT running

**To start backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test the API Directly
Open browser and go to: `http://127.0.0.1:8000/api/opportunities`
- ✅ Should show JSON array of opportunities
- ❌ If you see error → Check backend console for errors

### 3. Check Frontend Console
1. Open your app in browser (`http://localhost:5173`)
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Look for red errors
5. Go to **Network** tab
6. Refresh the page
7. Look for the request to `/api/opportunities`
   - Click on it
   - Check the **Response** tab
   - Check the **Preview** tab

### 4. Common Issues & Fixes

#### Issue: "CORS Error"
**Symptom**: Console shows "blocked by CORS policy"
**Fix**: Backend `main.py` should have:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: "500 Internal Server Error"
**Symptom**: Network tab shows status 500
**Fix**: Check backend console for Python error traceback

#### Issue: "404 Not Found"
**Symptom**: Network tab shows status 404
**Fix**: 
- Verify backend is running
- Check URL is correct: `http://127.0.0.1:8000/api/opportunities`

#### Issue: "Empty Array []"
**Symptom**: API returns `[]` (empty array)
**Fix**: No opportunities in database
- Run the sync: `POST http://127.0.0.1:8000/api/sync-force`
- Or check database: `SELECT COUNT(*) FROM opportunity;`

#### Issue: "Loading forever"
**Symptom**: Dashboard shows loading spinner forever
**Fix**: 
- Check if `fetchOpportunities()` is being called
- Check if there's a JavaScript error in console
- Verify the fetch URL matches backend URL

### 5. Manual Database Check

Open PostgreSQL client and run:
```sql
-- Check if opportunities exist
SELECT COUNT(*) FROM opportunity;

-- Check workflow_status
SELECT workflow_status, COUNT(*) 
FROM opportunity 
GROUP BY workflow_status;

-- See sample data
SELECT opp_id, opp_name, workflow_status 
FROM opportunity 
LIMIT 5;
```

### 6. Check Backend Logs

Look at your backend terminal window. You should see:
```
INFO:     127.0.0.1:XXXXX - "GET /api/opportunities HTTP/1.1" 200 OK
```

If you see:
```
ERROR: ...
```
Copy the full error message.

---

## Step-by-Step Diagnostic

1. **Open 3 terminal windows:**
   - Terminal 1: Backend
   - Terminal 2: Frontend  
   - Terminal 3: Testing

2. **Terminal 1 - Start Backend:**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend"
python -m uvicorn app.main:app --reload
```
Wait for: `Uvicorn running on http://127.0.0.1:8000`

3. **Terminal 2 - Start Frontend:**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\frontend"
npm run dev
```
Wait for: `Local: http://localhost:5173/`

4. **Terminal 3 - Test API:**
```bash
curl http://127.0.0.1:8000/api/opportunities
```
Should show JSON data.

5. **Open Browser:**
   - Go to `http://localhost:5173`
   - Open DevTools (F12)
   - Watch Console and Network tabs
   - Try to load dashboard

---

## What to Report

If still not working, please provide:

1. **Backend console output** (last 20 lines)
2. **Frontend console errors** (screenshot or copy)
3. **Network tab** (screenshot of the failed request)
4. **Database query results**:
   ```sql
   SELECT COUNT(*) FROM opportunity;
   ```

This will help me identify the exact issue!
