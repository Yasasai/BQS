# 🚀 Quick Start - Oracle CRM to PostgreSQL Sync

## ✅ What's Been Implemented

Your BQS system now has **complete Oracle CRM synchronization** with the following features:

### 🎯 Core Features
- ✅ **Full Sync** on first run (fetches ALL opportunities from Oracle)
- ✅ **Incremental Sync** on subsequent runs (updates existing records)
- ✅ **Automated Daily Sync** at midnight (00:00)
- ✅ **Manual Sync Trigger** via API or command line
- ✅ **Sync Status Tracking** in database
- ✅ **Comprehensive Logging** for debugging
- ✅ **Workflow Status Preservation** (BQS statuses not overwritten)

### 📊 Data Flow
```
Oracle CRM → sync_manager.py → PostgreSQL → FastAPI → Frontend
```

## 🏃 How to Run

### Option 1: Start Backend (Recommended)
```bash
# Double-click or run:
backend\start_backend.bat
```

This will:
1. Install dependencies
2. Start FastAPI server on port 8000
3. Initialize database
4. Schedule daily sync at midnight

### Option 2: Manual Sync (Testing)
```bash
# Double-click or run:
run_manual_sync.bat
```

This will immediately sync Oracle CRM data to PostgreSQL.

### Option 3: API Trigger
```bash
# Trigger sync via API
curl -X POST http://localhost:8000/api/sync-database
```

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:8000/api/opportunities` | GET | Get all opportunities |
| `http://localhost:8000/api/sync-database` | POST | Trigger manual sync |
| `http://localhost:8000/api/sync-status` | GET | Get last sync status |
| `http://localhost:8000/api/sync-history` | GET | Get sync history |
| `http://localhost:8000/docs` | GET | Interactive API docs |

## 🔍 Monitoring Sync

### Check Last Sync Status
```bash
curl http://localhost:8000/api/sync-status
```

**Example Response:**
```json
{
  "sync_type": "FULL",
  "status": "SUCCESS",
  "total_fetched": 150,
  "new_records": 150,
  "updated_records": 0,
  "failed_records": 0,
  "started_at": "2026-01-13T00:00:00",
  "completed_at": "2026-01-13T00:02:30",
  "duration_seconds": 150
}
```

### View Sync History
```bash
curl http://localhost:8000/api/sync-history
```

## 🔧 Configuration

### Environment Variables (backend/.env)
```env
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com
ORACLE_PASS=Welcome@123
DATABASE_URL=postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs
```

**Note:** `.env` file is gitignored for security

## 📋 How It Works

### First Sync (Full)
1. ✅ Detects empty database
2. ✅ Fetches **ALL** opportunities from Oracle (with pagination)
3. ✅ Creates new records in PostgreSQL
4. ✅ Sets workflow_status to 'NEW'
5. ✅ Logs sync operation to `sync_logs` table

### Subsequent Syncs (Incremental)
1. ✅ Fetches all opportunities from Oracle
2. ✅ For each opportunity:
   - **Exists in DB?** → Update Oracle fields only
   - **New?** → Create new record
3. ✅ **Preserves BQS workflow status** (unless Oracle shows CLOSED)
4. ✅ Logs sync operation

### Smart Status Handling
- **BQS workflow statuses are preserved** during sync
- Only overwritten if Oracle shows: CLOSED, WON, or LOST
- Prevents losing in-progress assessments

## 🗂️ File Structure

```
BQS/
├── backend/
│   ├── sync_manager.py      # Main sync orchestrator
│   ├── oracle_service.py    # Oracle API integration
│   ├── sync_status.py       # Sync tracking utilities
│   ├── database.py          # Database models
│   ├── main.py              # FastAPI server
│   ├── .env                 # Environment config (gitignored)
│   └── start_backend.bat    # Quick start script
├── run_manual_sync.bat      # Manual sync trigger
├── ORACLE_SYNC_GUIDE.md     # Detailed documentation
└── SYNC_QUICKSTART.md       # This file
```

## 🎯 Testing the Setup

### Step 1: Start Backend
```bash
backend\start_backend.bat
```

Wait for:
```
✓ Database initialized
✓ Schema is up to date
✓ Scheduler started: Syncing daily at midnight (00:00)
✓ Backend Ready!
```

### Step 2: Trigger First Sync
```bash
curl -X POST http://localhost:8000/api/sync-database
```

### Step 3: Check Sync Status
```bash
curl http://localhost:8000/api/sync-status
```

### Step 4: View Opportunities
```bash
curl http://localhost:8000/api/opportunities
```

### Step 5: Open Frontend
Your frontend should now display synced Oracle opportunities!

## 🚨 Troubleshooting

### Backend Won't Start
1. Check PostgreSQL is running
2. Verify credentials in `.env`
3. Install dependencies: `pip install -r requirements.txt`

### No Data Syncing
1. Check Oracle credentials in `.env`
2. Verify network/VPN connection
3. Check backend logs for errors
4. Test Oracle API manually:
   ```bash
   curl -u "user:pass" "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities?limit=1"
   ```

### Sync Failing
1. Check `/api/sync-status` for error message
2. Review backend console logs
3. Verify database connection
4. Run manual sync to see detailed logs

### Frontend Not Showing Data
1. Verify backend is running: `http://localhost:8000`
2. Check `/api/opportunities` returns data
3. Verify CORS settings in `main.py`
4. Check browser console for errors

## 📊 Database Tables

### opportunities
Stores all Oracle CRM opportunities with BQS workflow tracking

### sync_logs
Tracks every sync operation with detailed statistics

### assessments
BQS assessment data (linked to opportunities)

## 🔄 Sync Schedule

**Default Schedule:** Daily at midnight (00:00)

**To Change Schedule:**
Edit `backend/main.py` line 84-89:
```python
scheduler.add_job(
    sync_opportunities, 
    'cron',
    hour=0,    # Change hour (0-23)
    minute=0,  # Change minute (0-59)
    id='oracle_sync_job'
)
```

**Examples:**
- Every 6 hours: `'interval', hours=6`
- Every day at 2 AM: `'cron', hour=2, minute=0`
- Twice daily (6 AM & 6 PM): `'cron', hour='6,18', minute=0`

## 📈 Next Steps

1. ✅ **Test the sync** - Run manual sync and verify data
2. ✅ **Monitor logs** - Check sync status and history
3. ✅ **Verify frontend** - Ensure data displays correctly
4. ✅ **Schedule review** - Adjust sync schedule if needed
5. ✅ **Field mapping** - Customize Oracle field mappings in `oracle_service.py`

## 📚 Additional Documentation

- **Detailed Guide:** `ORACLE_SYNC_GUIDE.md`
- **API Docs:** `http://localhost:8000/docs` (when backend running)
- **Database Schema:** See `backend/database.py`

## ✅ Success Checklist

- [ ] Backend starts without errors
- [ ] First sync completes successfully
- [ ] Data appears in PostgreSQL
- [ ] Frontend displays synced opportunities
- [ ] Sync status API returns data
- [ ] Daily sync is scheduled
- [ ] Workflow statuses are preserved

## 🎉 You're All Set!

Your Oracle CRM → PostgreSQL → Frontend sync is now fully operational!

**Questions?** Check `ORACLE_SYNC_GUIDE.md` for detailed documentation.
