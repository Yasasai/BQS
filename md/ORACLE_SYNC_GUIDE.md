# Oracle CRM to PostgreSQL Sync - Complete Guide

## 🎯 Overview

This system automatically synchronizes data from Oracle CRM to PostgreSQL database and serves it to the frontend application.

**Data Flow:**
```
Oracle CRM → sync_manager.py → PostgreSQL → FastAPI → Frontend
```

## 🔧 Components

### 1. **sync_manager.py**
- **Purpose**: Orchestrates the sync process
- **Features**:
  - ✅ Full sync on first run (fetches all opportunities)
  - ✅ Incremental sync on subsequent runs (only updated records)
  - ✅ Robust error handling with per-record commits
  - ✅ Detailed logging and progress tracking
  - ✅ Preserves BQS workflow status unless Oracle shows closed

### 2. **oracle_service.py**
- **Purpose**: Handles Oracle CRM API communication
- **Features**:
  - ✅ Pagination support (fetches ALL opportunities)
  - ✅ Extended field mapping
  - ✅ Timeout and retry handling
  - ✅ Comprehensive error logging

### 3. **sync_status.py**
- **Purpose**: Tracks sync operations in database
- **Features**:
  - ✅ Logs each sync operation
  - ✅ Tracks success/failure status
  - ✅ Records sync statistics
  - ✅ Provides sync history

### 4. **main.py (FastAPI)**
- **Purpose**: Serves data to frontend
- **Endpoints**:
  - `GET /api/opportunities` - Get all opportunities
  - `POST /api/sync-database` - Trigger manual sync
  - `GET /api/sync-status` - Get last sync status
  - `GET /api/sync-history` - Get sync history

### 5. **database.py**
- **Models**:
  - `Opportunity` - Stores Oracle opportunities
  - `SyncLog` - Tracks sync operations
  - `Assessment` - BQS assessments
  - `User` - User management

## ⚙️ Configuration

### Environment Variables (.env)
```env
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_USER=yasasvi.upadrasta@inspiraenterprise.com
ORACLE_PASS=Welcome@123
DATABASE_URL=postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs
```

## 🚀 How It Works

### First Sync (Full)
1. System detects empty database
2. Fetches **ALL** opportunities from Oracle CRM (with pagination)
3. Creates new records in PostgreSQL
4. Sets workflow_status to 'NEW'
5. Logs sync operation

### Subsequent Syncs (Incremental)
1. Fetches all opportunities from Oracle
2. For each opportunity:
   - If exists in DB: **UPDATE** Oracle fields
   - If new: **CREATE** new record
3. Preserves BQS workflow status unless Oracle shows closed
4. Logs sync operation

### Field Mapping
| Oracle Field | PostgreSQL Field | Notes |
|--------------|------------------|-------|
| OptyId | remote_id | Unique identifier |
| Name | name | Opportunity name |
| TargetPartyName | customer | Account name |
| Revenue | deal_value | Deal value |
| CurrencyCode | currency | Currency code |
| WinProb | win_probability | Win probability % |
| SalesStage | stage | Sales stage |
| EffectiveDate | close_date | Expected close date |
| OwnerResourcePartyId | sales_owner | Owner ID |

## 📅 Automated Scheduling

**Schedule**: Daily at midnight (00:00)
**Scheduler**: APScheduler with cron trigger

```python
scheduler.add_job(
    sync_opportunities, 
    'cron',
    hour=0,
    minute=0,
    id='oracle_sync_job'
)
```

## 🔍 Monitoring

### Check Last Sync Status
```bash
curl http://localhost:8000/api/sync-status
```

Response:
```json
{
  "sync_type": "INCREMENTAL",
  "status": "SUCCESS",
  "total_fetched": 150,
  "new_records": 5,
  "updated_records": 145,
  "failed_records": 0,
  "started_at": "2026-01-13T06:30:00",
  "completed_at": "2026-01-13T06:32:15",
  "duration_seconds": 135
}
```

### View Sync History
```bash
curl http://localhost:8000/api/sync-history?limit=10
```

## 🛠️ Manual Operations

### Trigger Manual Sync
```bash
curl -X POST http://localhost:8000/api/sync-database
```

### Run Sync from Command Line
```bash
cd backend
python sync_manager.py
```

## 🔒 Data Integrity

### Workflow Status Preservation
- BQS workflow statuses are **preserved** during sync
- Only overwritten if Oracle shows opportunity as CLOSED/WON/LOST
- Prevents losing in-progress assessments

### Error Handling
- Each record commits individually
- Failed records logged but don't stop sync
- Partial results returned on timeout
- Detailed error logging for debugging

## 📊 Database Schema

### opportunities table
```sql
- id (PK)
- remote_id (Oracle OptyId, unique)
- name
- customer
- practice
- geo, region, sector
- deal_value, currency
- win_probability
- sales_owner
- stage
- workflow_status (BQS internal)
- close_date
- last_synced_at
```

### sync_logs table
```sql
- id (PK)
- sync_type (FULL/INCREMENTAL)
- status (RUNNING/SUCCESS/FAILED)
- total_fetched
- new_records
- updated_records
- failed_records
- error_message
- started_at
- completed_at
- duration_seconds
```

## 🚨 Troubleshooting

### No Data Syncing
1. Check Oracle credentials in `.env`
2. Verify network/VPN connection to Oracle
3. Check backend logs for errors
4. Test Oracle API manually:
   ```bash
   curl -u "user:pass" "https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities?limit=1"
   ```

### Sync Failing
1. Check `/api/sync-status` for error message
2. Review backend logs
3. Verify database connection
4. Check disk space

### Frontend Not Showing Data
1. Verify backend is running: `http://localhost:8000`
2. Check `/api/opportunities` endpoint
3. Verify CORS settings in main.py
4. Check browser console for errors

## 🎯 Next Steps

### Recommended Enhancements
1. **Email Notifications**: Alert on sync failures
2. **Webhook Support**: Trigger sync on Oracle events
3. **Delta Sync**: Only fetch changed records (requires Oracle LastUpdateDate filter)
4. **Retry Logic**: Auto-retry failed records
5. **Performance Metrics**: Track sync performance over time

## 📝 Maintenance

### Daily Tasks
- Monitor sync status via `/api/sync-status`
- Check for failed records

### Weekly Tasks
- Review sync history
- Check database size
- Verify data accuracy

### Monthly Tasks
- Review and optimize sync performance
- Update field mappings if Oracle schema changes
- Archive old sync logs

## 🔗 API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/opportunities` | GET | Get all opportunities |
| `/api/oracle-opportunity/{id}` | GET | Get single opportunity |
| `/api/sync-database` | POST | Trigger manual sync |
| `/api/sync-status` | GET | Get last sync status |
| `/api/sync-history` | GET | Get sync history |

## ✅ Success Criteria

- ✅ First sync fetches all Oracle opportunities
- ✅ Subsequent syncs are incremental
- ✅ Sync runs automatically daily at midnight
- ✅ Frontend displays synced data
- ✅ Workflow statuses preserved
- ✅ All sync operations logged
- ✅ Error handling prevents data loss
