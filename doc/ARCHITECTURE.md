# BQS System Architecture & File Interrelations

## 📊 Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │   SETUP PHASE  │       │   RUN PHASE    │
            └───────┬────────┘       └───────┬────────┘
                    │                        │
                    │                        │
┌───────────────────▼────────────────────────▼───────────────────┐
│                    PROJECT ROOT (BQS/)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📄 .env                    ← Environment configuration         │
│  📄 README.md               ← Project documentation             │
│  📄 fix_install.py          ← Quick dependency fixer            │
│  📄 cleanup_project.py      ← This cleanup script               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📁 backend/                                             │  │
│  │  ├── 📄 requirements.txt    ← Python dependencies        │  │
│  │  ├── 📄 __init__.py                                      │  │
│  │  ├── 📁 venv/               ← Virtual environment        │  │
│  │  │                                                        │  │
│  │  └── 📁 app/                ← MAIN APPLICATION           │  │
│  │      ├── 📄 __init__.py                                  │  │
│  │      ├── 📄 main.py         ← FastAPI entry point       │  │
│  │      ├── 📄 models.py       ← Database models           │  │
│  │      │                                                   │  │
│  │      ├── 📁 core/           ← Core utilities            │  │
│  │      │   ├── database.py    ← DB connection & init      │  │
│  │      │   └── constants.py   ← Shared enums              │  │
│  │      │                                                   │  │
│  │      ├── 📁 routers/        ← API endpoints             │  │
│  │      │   ├── auth.py        ← User management           │  │
│  │      │   ├── inbox.py       ← Opportunity inbox         │  │
│  │      │   └── scoring.py     ← Assessment scoring        │  │
│  │      │                                                   │  │
│  │      └── 📁 services/       ← Business logic            │  │
│  │          ├── oracle_service.py  ← Oracle API calls      │  │
│  │          └── sync_manager.py    ← Data sync logic       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📁 frontend/                                            │  │
│  │  ├── 📁 src/                ← React components          │  │
│  │  ├── 📁 public/             ← Static assets             │  │
│  │  ├── 📄 package.json        ← Node dependencies         │  │
│  │  └── 📄 vite.config.ts      ← Build configuration       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📁 scripts/                                             │  │
│  │  ├── 📁 setup/                                           │  │
│  │  │   └── setup_project.py  ← Universal setup script     │  │
│  │  └── 📁 util/               ← Debugging utilities        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📁 doc/                                                 │  │
│  │  ├── PROJECT_CLEANUP_PLAN.md                            │  │
│  │  └── ARCHITECTURE.md                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Diagram

```
┌─────────────────┐
│   Oracle CRM    │  (External System)
│  Opportunities  │
└────────┬────────┘
         │
         │ HTTPS API Calls
         │ (Basic Auth / OAuth2)
         ▼
┌─────────────────────────────────────────┐
│  backend/app/services/oracle_service.py │
│  ─────────────────────────────────────  │
│  • get_oracle_token()                   │
│  • get_from_oracle()                    │
│  • get_all_opportunities()              │
│  • fetch_single_opportunity()           │
└────────┬────────────────────────────────┘
         │
         │ Raw JSON data
         ▼
┌─────────────────────────────────────────┐
│  backend/app/services/sync_manager.py   │
│  ─────────────────────────────────────  │
│  • map_oracle_to_db()                   │
│  • sync_opportunities()                 │
│  • Handles pagination                   │
│  • Upsert logic                         │
└────────┬────────────────────────────────┘
         │
         │ Mapped Python dicts
         ▼
┌─────────────────────────────────────────┐
│  backend/app/models.py                  │
│  ─────────────────────────────────────  │
│  • Opportunity (SQLAlchemy model)       │
│  • AppUser, Role, Practice              │
│  • OpportunityAssignment                │
│  • OppScoreVersion                      │
└────────┬────────────────────────────────┘
         │
         │ ORM operations
         ▼
┌─────────────────────────────────────────┐
│  backend/app/core/database.py           │
│  ─────────────────────────────────────  │
│  • init_db() - Create DB & tables       │
│  • SessionLocal - DB session factory    │
│  • get_db() - Dependency injection      │
└────────┬────────────────────────────────┘
         │
         │ SQL queries
         ▼
┌─────────────────────────────────────────┐
│        PostgreSQL Database              │
│        (localhost:5432/bqs)             │
│  ─────────────────────────────────────  │
│  Tables:                                │
│  • opportunity                          │
│  • app_user                             │
│  • role, user_role                      │
│  • practice                             │
│  • opportunity_assignment               │
│  • opp_score_version                    │
│  • opp_score_section                    │
│  • opp_score_section_value              │
│  • sync_run                             │
└────────┬────────────────────────────────┘
         │
         │ Query results
         ▼
┌─────────────────────────────────────────┐
│  backend/app/routers/                   │
│  ─────────────────────────────────────  │
│  • auth.py    → /api/auth/users         │
│  • inbox.py   → /api/inbox/unassigned   │
│  • scoring.py → /api/scoring/{id}       │
└────────┬────────────────────────────────┘
         │
         │ JSON responses
         ▼
┌─────────────────────────────────────────┐
│  backend/app/main.py (FastAPI)          │
│  ─────────────────────────────────────  │
│  • CORS middleware                      │
│  • Router registration                  │
│  • Lifespan events (startup sync)       │
│  • Runs on http://localhost:8000        │
└────────┬────────────────────────────────┘
         │
         │ HTTP requests
         ▼
┌─────────────────────────────────────────┐
│  frontend/ (React + TypeScript)         │
│  ─────────────────────────────────────  │
│  • Vite dev server                      │
│  • React components                     │
│  • API calls to backend                 │
│  • Runs on http://localhost:5173        │
└────────┬────────────────────────────────┘
         │
         │ Rendered UI
         ▼
┌─────────────────┐
│   Web Browser   │
│   (User View)   │
└─────────────────┘
```

## 🔧 Configuration Flow

```
┌─────────────────────────────────────────┐
│  .env (Root directory)                  │
│  ─────────────────────────────────────  │
│  ORACLE_BASE_URL=...                    │
│  ORACLE_USER=...                        │
│  ORACLE_PASSWORD=...                    │
│  DATABASE_URL=postgresql://...          │
└────────┬────────────────────────────────┘
         │
         │ Loaded by python-dotenv
         ├──────────────┬─────────────┐
         ▼              ▼             ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐
│oracle_service│  │database  │  │sync_mgr  │
│    .py       │  │   .py    │  │   .py    │
└──────────────┘  └──────────┘  └──────────┘
         │              │             │
         └──────────────┴─────────────┘
                        │
                        ▼
              Application Runtime
```

## 🚀 Startup Sequence

```
1. User runs: python scripts/setup/setup_project.py --with-data
   │
   ├─▶ Check Python/Node installed
   ├─▶ Create backend/venv
   ├─▶ Install backend/requirements.txt
   ├─▶ Install frontend/package.json
   │
   ├─▶ Call: backend.app.core.database.init_db()
   │   ├─▶ Connect to PostgreSQL
   │   ├─▶ Create 'bqs' database if missing
   │   ├─▶ Create all tables from models.py
   │   └─▶ Seed initial data (Users, Roles, Sections)
   │
   └─▶ Call: backend.app.services.sync_manager.sync_opportunities()
       ├─▶ Fetch from Oracle CRM
       ├─▶ Map to database models
       └─▶ Upsert into PostgreSQL

2. User runs: python -m backend.app.main
   │
   ├─▶ Load backend/app/main.py
   ├─▶ Initialize FastAPI app
   ├─▶ Register routers (auth, inbox, scoring)
   ├─▶ Lifespan startup:
   │   ├─▶ Call init_db() (ensure DB ready)
   │   └─▶ Call sync_opportunities() (auto-sync)
   │
   └─▶ Start uvicorn server on :8000

3. User runs: npm run dev (in frontend/)
   │
   ├─▶ Start Vite dev server
   ├─▶ Compile React/TypeScript
   └─▶ Serve on :5173

4. User opens browser → http://localhost:5173
   │
   ├─▶ Frontend loads
   ├─▶ Makes API calls to :8000
   └─▶ Displays opportunities from database
```

## 📦 Module Dependencies

```
backend/app/main.py
  ├─ imports: backend.app.core.database (init_db, get_db)
  ├─ imports: backend.app.services.sync_manager (sync_opportunities)
  └─ imports: backend.app.routers.* (auth, inbox, scoring)

backend/app/routers/auth.py
  ├─ imports: backend.app.core.database (get_db)
  └─ imports: backend.app.models (AppUser, Role, UserRole)

backend/app/routers/inbox.py
  ├─ imports: backend.app.core.database (get_db)
  └─ imports: backend.app.models (Opportunity, OpportunityAssignment)

backend/app/routers/scoring.py
  ├─ imports: backend.app.core.database (get_db)
  └─ imports: backend.app.models (OppScoreVersion, OppScoreSection, ...)

backend/app/services/sync_manager.py
  ├─ imports: backend.app.core.database (SessionLocal, init_db)
  └─ imports: backend.app.models (Opportunity, Practice)

backend/app/services/oracle_service.py
  ├─ imports: requests, python-dotenv
  └─ reads: .env file

backend/app/core/database.py
  ├─ imports: psycopg2, sqlalchemy
  ├─ imports: backend.app.models (Base, Role, AppUser, ...)
  └─ reads: .env file (DATABASE_URL)

backend/app/models.py
  ├─ imports: sqlalchemy
  └─ defines: All database table schemas
```

## 🎯 Key Integration Points

### 1. **Environment Variables (.env)**
   - Used by: `oracle_service.py`, `database.py`, `sync_manager.py`
   - Contains: Oracle credentials, Database URL
   - **Critical**: Must exist before running application

### 2. **Database Initialization (database.py)**
   - Called by: `main.py` (startup), `setup_project.py`
   - Creates: Database, tables, seed data
   - **Critical**: Must run before any DB operations

### 3. **Oracle Sync (sync_manager.py)**
   - Called by: `main.py` (startup), `setup_project.py`
   - Depends on: `oracle_service.py`, `database.py`, `models.py`
   - **Critical**: Populates database with real data

### 4. **API Routers**
   - Registered in: `main.py`
   - Depend on: `database.py` (get_db), `models.py`
   - **Critical**: Expose data to frontend

### 5. **Frontend Integration**
   - Calls: Backend API endpoints (:8000)
   - Displays: Data from PostgreSQL via FastAPI
   - **Critical**: Must match backend API contracts

## ✅ What You Need to Know

### **To Start Development:**
1. Ensure `.env` exists with correct credentials
2. Run `python scripts/setup/setup_project.py --with-data`
3. Start backend: `python -m backend.app.main`
4. Start frontend: `npm run dev` (in frontend/)

### **To Add a New Feature:**
1. **New Database Table**: Add to `models.py`
2. **New API Endpoint**: Add to appropriate router in `routers/`
3. **New Business Logic**: Add to `services/`
4. **New Frontend Page**: Add to `frontend/src/`

### **To Debug Issues:**
1. **Database**: Check `backend/app/core/database.py`
2. **Oracle Sync**: Check `backend/app/services/sync_manager.py`
3. **API**: Check `backend/app/routers/`
4. **Frontend**: Check browser console + `frontend/src/`

### **Files You'll Edit Most:**
- `backend/app/routers/*.py` - API endpoints
- `backend/app/models.py` - Database schema
- `frontend/src/` - UI components
- `.env` - Configuration

### **Files You Rarely Touch:**
- `backend/app/core/database.py` - DB setup (stable)
- `backend/app/services/oracle_service.py` - Oracle API (stable)
- `scripts/setup/setup_project.py` - Setup (stable)
