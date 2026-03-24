# Oracle CRM Sync - System Architecture

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORACLE CRM CLOUD                          │
│  https://eijs-test.fa.em2.oraclecloud.com/crmRestApi            │
│                                                                   │
│  Opportunities Data:                                             │
│  - OptyId, Name, Customer                                        │
│  - Revenue, Currency, Win Probability                            │
│  - Sales Stage, Owner, Close Date                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS REST API
                         │ (HTTPBasicAuth)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORACLE_SERVICE.PY                             │
│                                                                   │
│  ✓ Pagination (fetch ALL opportunities)                         │
│  ✓ Field mapping (Oracle → PostgreSQL)                          │
│  ✓ Error handling & retries                                     │
│  ✓ Timeout management                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Python Dict
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNC_MANAGER.PY                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FIRST SYNC (Full)                                        │  │
│  │  1. Detect empty database                                 │  │
│  │  2. Fetch ALL opportunities                               │  │
│  │  3. Create new records                                    │  │
│  │  4. Set workflow_status = 'NEW'                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SUBSEQUENT SYNCS (Incremental)                           │  │
│  │  1. Fetch all opportunities                               │  │
│  │  2. For each:                                             │  │
│  │     - Exists? → UPDATE Oracle fields                      │  │
│  │     - New? → CREATE record                                │  │
│  │  3. Preserve BQS workflow status                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ✓ Per-record commits (resilience)                              │
│  ✓ Detailed logging                                              │
│  ✓ Sync statistics tracking                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQLAlchemy ORM
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
│                    (localhost:5432/bqs)                          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  opportunities                                          │    │
│  │  - id, remote_id (Oracle OptyId)                       │    │
│  │  - name, customer, practice, geo                       │    │
│  │  - deal_value, currency, win_probability               │    │
│  │  - stage, sales_owner, close_date                      │    │
│  │  - workflow_status (BQS internal)                      │    │
│  │  - last_synced_at                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  sync_logs                                              │    │
│  │  - sync_type (FULL/INCREMENTAL)                        │    │
│  │  - status (SUCCESS/FAILED)                             │    │
│  │  - total_fetched, new_records, updated_records         │    │
│  │  - started_at, completed_at, duration_seconds          │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQLAlchemy ORM
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI (main.py)                             │
│                    http://localhost:8000                         │
│                                                                   │
│  API Endpoints:                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  GET  /api/opportunities        → List all            │    │
│  │  GET  /api/oracle-opportunity/{id} → Get single       │    │
│  │  POST /api/sync-database        → Trigger sync        │    │
│  │  GET  /api/sync-status          → Last sync status    │    │
│  │  GET  /api/sync-history         → Sync history        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Scheduler (APScheduler):                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Cron Job: Daily at 00:00                              │    │
│  │  Triggers: sync_opportunities()                        │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/JSON (CORS enabled)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND APPLICATION                          │
│                    http://localhost:5173                         │
│                                                                   │
│  Components:                                                     │
│  - Dashboard (displays opportunities)                            │
│  - OpportunityInbox (list view)                                 │
│  - AssessmentForm (detail view)                                 │
│  - SyncStatusBanner (sync monitoring)                           │
│                                                                   │
│  Features:                                                       │
│  ✓ Real-time data from PostgreSQL                               │
│  ✓ Workflow management                                           │
│  ✓ Assessment tracking                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Sync Flow Sequence

```
1. SCHEDULED TRIGGER (Daily at 00:00)
   │
   ├─→ APScheduler calls sync_opportunities()
   │
2. SYNC MANAGER INITIALIZATION
   │
   ├─→ Create SyncLog entry (status: RUNNING)
   ├─→ Check if first sync (database empty?)
   │
3. ORACLE API CALL
   │
   ├─→ oracle_service.get_oracle_opportunities()
   ├─→ Pagination loop (fetch all batches)
   ├─→ Return list of opportunities
   │
4. DATA PROCESSING
   │
   ├─→ For each opportunity:
   │   ├─→ map_oracle_to_db() (field mapping)
   │   ├─→ Check if exists in PostgreSQL
   │   ├─→ If exists: UPDATE (preserve workflow_status)
   │   ├─→ If new: INSERT (set workflow_status = 'NEW')
   │   └─→ Commit transaction
   │
5. SYNC COMPLETION
   │
   ├─→ Calculate statistics
   ├─→ Update SyncLog (status: SUCCESS/FAILED)
   ├─→ Log summary to console
   │
6. FRONTEND ACCESS
   │
   └─→ Frontend calls /api/opportunities
       └─→ Displays synced data
```

## 🔐 Data Integrity Rules

### Workflow Status Preservation
```
Oracle Status     →  Action on PostgreSQL
─────────────────────────────────────────
OPEN              →  Preserve BQS workflow_status
QUALIFIED         →  Preserve BQS workflow_status
PROPOSAL          →  Preserve BQS workflow_status
CLOSED WON        →  Set workflow_status = 'CLOSED_IN_CRM'
CLOSED LOST       →  Set workflow_status = 'CLOSED_IN_CRM'
```

### Field Update Rules
```
Field Type        →  Update Strategy
─────────────────────────────────────────
Oracle Fields     →  Always update from Oracle
(name, customer,      (source of truth)
deal_value, etc.)

BQS Fields        →  Never overwrite
(workflow_status,     (unless Oracle closed)
assigned_sa,
sa_notes, etc.)
```

## ⚡ Performance Characteristics

- **Pagination**: 500 records per API call
- **Commit Strategy**: Per-record (resilience over speed)
- **Timeout**: 90 seconds per API call
- **Retry**: Partial results on timeout
- **Typical Sync Time**: ~1-2 seconds per opportunity

## 🎯 Key Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **oracle_service.py** | Oracle API integration | Pagination, field mapping, error handling |
| **sync_manager.py** | Sync orchestration | Full/incremental logic, logging, stats |
| **sync_status.py** | Sync tracking | Database logging, history, status queries |
| **database.py** | Data models | Opportunity, SyncLog, Assessment models |
| **main.py** | API server | REST endpoints, scheduler, CORS |

## 📊 Monitoring Points

1. **Sync Status**: `/api/sync-status`
2. **Sync History**: `/api/sync-history`
3. **Backend Logs**: Console output
4. **Database**: `sync_logs` table
5. **Opportunity Count**: `/api/opportunities`

## 🚀 Deployment Checklist

- [x] Oracle credentials configured
- [x] PostgreSQL running
- [x] Dependencies installed
- [x] Database initialized
- [x] Scheduler configured
- [x] CORS enabled for frontend
- [x] Error handling implemented
- [x] Logging configured
- [x] Sync tracking enabled
