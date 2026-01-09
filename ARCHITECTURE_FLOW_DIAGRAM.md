# BQS Platform - Business Flow to System Mapping
## Visual Architecture Guide

**Last Updated:** 2026-01-09

---

## 🔄 End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STEP 1: OPPORTUNITY ENTERING                        │
│                              (Oracle CRM Sync)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   Oracle CX Sales Cloud API     │
                    │   (REST API with OAuth)         │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   oracle_service.py             │
                    │   - get_oracle_opportunities()  │
                    │   - map_oracle_to_db()          │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   sync_manager.py               │
                    │   - Upsert logic                │
                    │   - Error handling              │
                    │   - Logging                     │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   PostgreSQL Database           │
                    │   Table: opportunities          │
                    │   - remote_id (Oracle ID)       │
                    │   - last_synced_at (watermark)  │
                    └─────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: INITIAL MANAGEMENT SCREENING                      │
│                           (Management Inbox)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   GET /api/opportunities        │
                    │   (FastAPI Endpoint)            │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   OpportunityInbox.tsx          │
                    │   - Tab filtering (All/Unassigned/Assigned/High Value)
                    │   - Search (name, customer, practice)
                    │   - Filters (Geo, Stage, Practice)
                    │   - Bulk selection              │
                    │   - Sync button                 │
                    └─────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 3: SA ASSIGNMENT                                │
│                    (Assign Solution Architect)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   AssignArchitectModal.tsx      │
                    │   - SA selection dropdown       │
                    │   - Priority (High/Med/Low)     │
                    │   - Notes field                 │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   POST /api/opportunities/{id}/assign  ⚠️ TO BE CREATED
                    │   (Backend API)                 │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   PostgreSQL Database           │
                    │   Table: opportunity_assignments ⚠️ TO BE CREATED
                    │   - opp_id                      │
                    │   - assigned_to (SA)            │
                    │   - assigned_by (Manager)       │
                    │   - is_active (enforce 1 active)│
                    │   - revoked_at (history)        │
                    └─────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STEP 4: EVALUATION & FEASIBILITY SCORING                   │
│                          (SA Inbox & Scoring)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   AssignedToMe.tsx              │
                    │   (SA Inbox)                    │
                    │   - Filter: Not Started/In Progress/Completed
                    │   - Click to view details       │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   OpportunityDetail.tsx         │
                    │   - Full Oracle context         │
                    │   - Customer info               │
                    │   - Deal value                  │
                    │   - "Score Opportunity" button  │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   ScoreOpportunity.tsx          │
                    │   - Strategic Fit (1-5)         │
                    │   - Delivery Feasibility (1-5)  │
                    │   - Commercial Viability (1-5)  │
                    │   - Risk Assessment (1-5)       │
                    │   - Notes per section           │
                    │   - Document upload             │
                    │   - Save Draft / Submit         │
                    └─────────────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
        ┌─────────────────────────┐   ┌─────────────────────────┐
        │ POST /api/assessments   │   │ POST /api/assessments/  │
        │ (Save Draft)            │   │ {id}/submit             │
        │ ⚠️ TO BE CREATED         │   │ (Lock & Submit)         │
        │                         │   │ ⚠️ TO BE CREATED         │
        └─────────────────────────┘   └─────────────────────────┘
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                    ┌─────────────────────────────────┐
                    │   PostgreSQL Database           │
                    │   Table: assessments ✅         │
                    │   - opp_id                      │
                    │   - version (versioning)        │
                    │   - scores (JSON)               │
                    │   - is_submitted (lock)         │
                    │   - created_at                  │
                    │   - created_by                  │
                    └─────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     STEP 5: LEADERSHIP & GOVERNANCE                          │
│                        (Decision Governance)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   GET /api/assessments/submitted│
                    │   ⚠️ TO BE CREATED               │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   LeadershipDashboard.tsx       │
                    │   ⚠️ TO BE CREATED               │
                    │   - View all submitted assessments
                    │   - Filter by date, SA, score   │
                    │   - Drill down into details     │
                    │   - View documents              │
                    │   - Track evaluator & timestamp │
                    │   - Approve/Reject/Request Rev. │
                    └─────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STEP 6: PROPOSAL & CLOSURE                              │
│                    (Traceability & Institutional Memory)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   Oracle CRM                    │
                    │   (Handles proposal & closure)  │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   Continuous Sync               │
                    │   (sync_manager.py)             │
                    │   - Updates opportunity status  │
                    │   - Preserves all history       │
                    └─────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │   PostgreSQL Database           │
                    │   - opportunities (full history)│
                    │   - assessments (all versions)  │
                    │   - assignments (revoked, not deleted)
                    │   - Institutional memory ✅     │
                    └─────────────────────────────────┘
```

---

## 🗄️ Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              opportunities                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    INTEGER PRIMARY KEY                                   │
│ remote_id             STRING UNIQUE (Oracle OptyId)                         │
│ name                  STRING                                                │
│ customer              STRING                                                │
│ practice              STRING                                                │
│ geo                   STRING                                                │
│ deal_value            FLOAT                                                 │
│ currency              STRING                                                │
│ win_probability       FLOAT                                                 │
│ sales_owner           STRING                                                │
│ stage                 STRING                                                │
│ close_date            DATETIME                                              │
│ rfp_date              DATETIME                                              │
│ last_updated_in_crm   DATETIME                                              │
│ last_synced_at        DATETIME (watermark for incremental sync)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1:N
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         opportunity_assignments ⚠️ TO BE CREATED             │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    INTEGER PRIMARY KEY                                   │
│ opp_id                INTEGER FOREIGN KEY → opportunities.id                │
│ assigned_to           STRING (SA email/name)                                │
│ assigned_by           STRING (Manager email/name)                           │
│ assigned_at           DATETIME                                              │
│ revoked_at            DATETIME (NULL if active)                             │
│ is_active             BOOLEAN (only 1 active per opportunity)               │
│ priority              STRING (high, medium, low)                            │
│ notes                 TEXT                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1:N
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              assessments ✅                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    INTEGER PRIMARY KEY                                   │
│ opp_id                INTEGER FOREIGN KEY → opportunities.id                │
│ version               STRING (v1, v2, etc.)                                 │
│ scores                JSON {fit: 4, delivery: 3, commercial: 5, risk: 2}   │
│ comments              TEXT                                                  │
│ risks                 JSON                                                  │
│ is_submitted          BOOLEAN (locks version when true)                     │
│ created_at            DATETIME (draft creation)                             │
│ created_by            STRING (SA email/name)                                │
│ submitted_at          DATETIME ⚠️ TO BE ADDED                               │
│ weighted_score        FLOAT (0-100) ⚠️ TO BE ADDED                          │
│ confidence_level      STRING ⚠️ TO BE ADDED                                 │
│ recommendation        STRING (Pursue/Caution/No-Bid) ⚠️ TO BE ADDED         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1:N
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            documents ⚠️ TO BE CREATED                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    INTEGER PRIMARY KEY                                   │
│ assessment_id         INTEGER FOREIGN KEY → assessments.id                  │
│ filename              STRING                                                │
│ file_path             STRING                                                │
│ file_size             INTEGER                                               │
│ uploaded_at           DATETIME                                              │
│ uploaded_by           STRING                                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                 users ✅                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ id                    INTEGER PRIMARY KEY                                   │
│ email                 STRING UNIQUE                                         │
│ name                  STRING                                                │
│ role                  STRING (Manager, SA, Leadership)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### ✅ Currently Implemented

```
GET  /                              - Health check
GET  /api/opportunities             - List all opportunities
GET  /api/oracle-opportunity/{id}   - Get opportunity detail
POST /api/sync-database             - Trigger Oracle sync (background)
```

### ⚠️ To Be Implemented

```
# Assignment APIs
POST /api/opportunities/{id}/assign           - Assign SA to opportunity
GET  /api/opportunities/{id}/assignment       - Get current assignment
GET  /api/opportunities/{id}/assignment-history - Get all assignments (incl. revoked)

# Assessment APIs
POST /api/assessments                         - Create draft assessment
PUT  /api/assessments/{id}                    - Update draft assessment
POST /api/assessments/{id}/submit             - Submit & lock assessment
GET  /api/opportunities/{id}/assessments      - Get all assessment versions
GET  /api/assessments/submitted               - Get all submitted (for leadership)
GET  /api/assessments/{id}                    - Get specific assessment

# Document APIs
POST /api/assessments/{id}/documents          - Upload document
GET  /api/assessments/{id}/documents          - List documents
DELETE /api/documents/{id}                    - Delete document

# Notification APIs
GET  /api/notifications                       - Get user notifications
POST /api/notifications/{id}/mark-read        - Mark notification as read
```

---

## 🎨 Frontend Pages & Routes

### ✅ Currently Implemented

```
/                       → OpportunityInbox.tsx      (Management Inbox)
/assigned-to-me         → AssignedToMe.tsx          (SA Inbox)
/opportunity/:id        → OpportunityDetail.tsx     (Opportunity Detail)
/score/:id              → ScoreOpportunity.tsx      (Scoring Interface)
```

### ⚠️ To Be Implemented

```
/leadership             → LeadershipDashboard.tsx   (Governance View)
/notifications          → Notifications.tsx         (Notification Center)
/reports                → Reports.tsx               (Analytics & Reports)
```

---

## 🔄 Data Flow Examples

### Example 1: Oracle Sync Flow

```
1. User clicks "Sync Database" button in OpportunityInbox.tsx
   ↓
2. Frontend calls: POST /api/sync-database
   ↓
3. Backend (main.py) triggers background task: sync_opportunities()
   ↓
4. sync_manager.py calls oracle_service.get_oracle_opportunities()
   ↓
5. oracle_service.py makes REST API call to Oracle CX Sales
   ↓
6. Oracle returns JSON with opportunities
   ↓
7. oracle_service.map_oracle_to_db() transforms data
   ↓
8. sync_manager.py upserts to PostgreSQL (opportunities table)
   ↓
9. last_synced_at timestamp updated
   ↓
10. Frontend shows success message
```

### Example 2: Assignment Flow (When Complete)

```
1. Manager selects opportunity in OpportunityInbox.tsx
   ↓
2. Clicks "Assign" button
   ↓
3. AssignArchitectModal.tsx opens
   ↓
4. Manager selects SA, priority, adds notes
   ↓
5. Clicks "Assign"
   ↓
6. Frontend calls: POST /api/opportunities/{id}/assign
   ↓
7. Backend checks for existing active assignment
   ↓
8. If exists: Sets revoked_at = now, is_active = false
   ↓
9. Creates new assignment record with is_active = true
   ↓
10. Returns success
   ↓
11. Frontend updates UI, shows assigned SA
   ↓
12. SA sees opportunity in AssignedToMe.tsx
```

### Example 3: Scoring Flow (When Complete)

```
1. SA opens opportunity in AssignedToMe.tsx
   ↓
2. Clicks "Score Opportunity"
   ↓
3. ScoreOpportunity.tsx loads
   ↓
4. SA scores 4 criteria (1-5), adds notes
   ↓
5. Clicks "Save Draft"
   ↓
6. Frontend calls: POST /api/assessments
   ↓
7. Backend creates assessment with is_submitted = false
   ↓
8. Returns assessment ID
   ↓
9. SA continues editing, clicks "Submit"
   ↓
10. Frontend calls: POST /api/assessments/{id}/submit
   ↓
11. Backend sets is_submitted = true, submitted_at = now
   ↓
12. Triggers notification to leadership
   ↓
13. Assessment appears in LeadershipDashboard.tsx
```

---

## 🔐 Security & Governance

### Current Implementation
- ✅ CORS configured for localhost:5173 (Vite)
- ✅ Database connection via environment variables
- ✅ Oracle API authentication (HTTPBasicAuth)

### To Be Implemented
- ⚠️ User authentication (JWT/OAuth)
- ⚠️ Role-based access control (RBAC)
- ⚠️ Audit logging for all actions
- ⚠️ Data encryption at rest
- ⚠️ API rate limiting

---

## 📊 Reporting & Analytics (Future)

### Potential Reports
- Opportunity pipeline by stage
- Assessment completion rate by SA
- Average scoring by practice/geo
- Time-to-assessment metrics
- Win/loss analysis
- SA workload distribution

---

## 🎯 Success Metrics

### System Performance
- Sync completion time < 5 minutes
- API response time < 500ms
- UI load time < 2 seconds
- 99.9% uptime

### Business Metrics
- % of opportunities assessed within 48 hours
- Assessment quality score
- Leadership decision time
- Win rate correlation with scores

---

**Legend:**
- ✅ Implemented and functional
- ⚠️ To be created/implemented
- 🔴 High priority
- 🟡 Medium priority
- 🟢 Low priority
