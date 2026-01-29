# BQS Project Cleanup & Consolidation Plan

## 📋 Current Status
Your project has **duplicate files** and **outdated scripts** scattered across multiple locations. This document identifies what to **KEEP**, what to **DELETE**, and how everything **interrelates**.

---

## ✅ ESSENTIAL FILES TO KEEP

### **Root Directory**
```
BQS/
├── .env                          # ✅ KEEP - Environment variables (Oracle credentials, DB config)
├── .gitignore                    # ✅ KEEP - Git exclusions
├── README.md                     # ✅ KEEP - Project documentation
├── fix_install.py                # ✅ KEEP - Quick dependency installer
└── requirements.txt              # ❌ DELETE - Duplicate (use backend/requirements.txt)
```

### **Backend Structure (NEW - Modular)**
```
backend/
├── __init__.py                   # ✅ KEEP - Package marker
├── requirements.txt              # ✅ KEEP - Python dependencies
├── .env.example                  # ✅ KEEP - Template for new developers
├── venv/                         # ✅ KEEP - Virtual environment
│
└── app/                          # ✅ KEEP - Main application code
    ├── __init__.py
    ├── main.py                   # ✅ KEEP - FastAPI entry point
    ├── models.py                 # ✅ KEEP - Database models (Opportunity, User, etc.)
    │
    ├── core/                     # ✅ KEEP - Core utilities
    │   ├── __init__.py
    │   ├── database.py           # ✅ KEEP - DB connection & initialization
    │   └── constants.py          # ✅ KEEP - Shared enums & constants
    │
    ├── routers/                  # ✅ KEEP - API endpoints
    │   ├── __init__.py
    │   ├── auth.py               # ✅ KEEP - User authentication
    │   ├── inbox.py              # ✅ KEEP - Opportunity inbox
    │   └── scoring.py            # ✅ KEEP - Assessment scoring
    │
    └── services/                 # ✅ KEEP - Business logic
        ├── __init__.py
        ├── oracle_service.py     # ✅ KEEP - Oracle CRM API integration
        └── sync_manager.py       # ✅ KEEP - Data synchronization
```

### **Frontend Structure**
```
frontend/                         # ✅ KEEP - React application (entire folder)
├── src/
├── public/
├── package.json
└── vite.config.ts
```

### **Scripts (Organized)**
```
scripts/
├── setup/
│   └── setup_project.py          # ✅ KEEP - Universal setup script
│
└── util/                         # ✅ KEEP - Utility scripts (optional)
    └── (debugging tools if needed)
```

### **Documentation**
```
doc/
├── PROJECT_CLEANUP_PLAN.md       # ✅ KEEP - This file
└── ARCHITECTURE.md               # ✅ KEEP - System architecture (move from root)
```

---

## ❌ FILES TO DELETE (Duplicates & Obsolete)

### **Root Directory - Delete These:**
```
❌ requirements.txt                    # Duplicate of backend/requirements.txt
❌ check_backend.py                    # Replaced by setup_project.py
❌ check_data.py                       # Obsolete debugging script
❌ create_env.py                       # Obsolete
❌ database_dump.json                  # Old data dump
❌ db_check_fast.py                    # Replaced by setup_project.py
❌ debug_oracle.py                     # Debugging - move to scripts/util if needed
❌ diagnose_sync.py                    # Debugging - move to scripts/util if needed
❌ diagnostic.py                       # Obsolete
❌ direct_api_test.py                  # Debugging - move to scripts/util if needed
❌ extract_names.py                    # Obsolete
❌ fetch_all_methods.py                # Obsolete
❌ fetch_by_names.py                   # Obsolete
❌ final_status_check.py               # Obsolete
❌ find_oracle_url.py                  # Obsolete
❌ fix_dotenv_finally.py               # Obsolete
❌ fix_install.bat                     # Keep .py version only
❌ heal_database.py                    # Replaced by backend/app/core/database.py
❌ oracle_api_config.txt               # Obsolete (use .env)
❌ populate_test_data.py               # Replaced by sync_manager.py
❌ prepare_github.bat                  # Obsolete
❌ probe_fields.py                     # Debugging - move to scripts/util if needed
❌ push_all.bat                        # Obsolete
❌ quick_db_probe.py                   # Obsolete
❌ quick_populate.py                   # Obsolete
❌ quick_verify_fix.py                 # Obsolete
❌ refined_sync_script.py              # Replaced by sync_manager.py
❌ run_manual_sync.bat                 # Obsolete
❌ run_sync.bat                        # Obsolete
❌ run_sync_now.bat                    # Obsolete
❌ seed_screenshot.py                  # Obsolete
❌ self_heal.py                        # Replaced by database.py init_db()
❌ setup_complete.bat                  # Replaced by setup_project.py
❌ setup_complete.py                   # Replaced by setup_project.py
❌ setup_data.bat                      # Obsolete
❌ setup_env.bat                       # Obsolete
❌ setup_now.py                        # Replaced by setup_project.py
❌ simple_sync.py                      # Replaced by sync_manager.py
❌ standardize_env.py                  # Obsolete
❌ sync_control_panel.html             # Obsolete (can recreate if needed)
❌ test_direct_oracle.py               # Debugging - move to scripts/util if needed
❌ test_oracle_connection.py           # Debugging - move to scripts/util if needed
❌ test_oracle_data.py                 # Debugging - move to scripts/util if needed
❌ test_oracle_permissions.py          # Debugging - move to scripts/util if needed
❌ trigger_sync.py                     # Obsolete
❌ trigger_sync_now.bat                # Obsolete
❌ update_env_aliases.py               # Obsolete
❌ verify_details.py                   # Obsolete
❌ verify_env.py                       # Obsolete
❌ SYNC_NOW.bat                        # Obsolete
```

### **Backend Directory - Delete These:**
```
backend/
❌ auto_heal.py                        # Replaced by app/core/database.py
❌ constants.py                        # Moved to app/core/constants.py
❌ database.py                         # Replaced by app/core/database.py
❌ dump_data.py                        # Move to scripts/util if needed
❌ inspect_oracle_fields.py            # Move to scripts/util if needed
❌ main.py                             # Replaced by app/main.py
❌ migrate_db.py                       # Replaced by app/core/database.py
❌ oracle_service.py                   # Replaced by app/services/oracle_service.py
❌ populate_dummy_data.py              # Obsolete
❌ quick_populate.py                   # Obsolete
❌ restore_data.py                     # Move to scripts/util if needed
❌ routers/                            # Replaced by app/routers/
❌ run_populate.bat                    # Obsolete
❌ start_backend.bat                   # Obsolete (use setup_project.py instructions)
❌ sync_manager.py                     # Replaced by app/services/sync_manager.py
❌ sync_status.py                      # Move to scripts/util if needed
❌ test_imports.py                     # Obsolete
```

### **Documentation - Consolidate These:**
```
❌ CLEANUP.md                          # Merge into this document
❌ EMERGENCY_GUIDE.md                  # Merge into README.md
❌ GITHUB_PUSH_CHECKLIST.md            # Merge into README.md
❌ GITHUB_PUSH_GUIDE.md                # Merge into README.md
❌ IMMEDIATE_SYNC_GUIDE.md             # Merge into README.md
❌ IMPLEMENTATION_SUMMARY.md           # Merge into ARCHITECTURE.md
❌ ORACLE_SYNC_GUIDE.md                # Merge into README.md
❌ PGADMIN_SCRIPT.txt                  # Move to doc/ if needed
❌ PUSH_SUMMARY.md                     # Obsolete
❌ SELF_HEAL.txt                       # Merge into README.md
❌ SETUP_GUIDE.md                      # Merge into README.md
❌ SQLALCHEMY_FIX.md                   # Obsolete
❌ SYNC_QUICKSTART.md                  # Merge into README.md
❌ TROUBLESHOOTING_TIMEOUT.md          # Merge into README.md
```

---

## 🔗 HOW EVERYTHING INTERRELATES

### **Application Flow**
```
1. User runs: python scripts/setup/setup_project.py --with-data
   ↓
2. Setup script:
   - Creates venv
   - Installs backend/requirements.txt
   - Installs frontend/package.json
   - Calls backend/app/core/database.py → init_db()
   - Calls backend/app/services/sync_manager.py → sync_opportunities()
   ↓
3. Database initialized with:
   - Tables (from backend/app/models.py)
   - Seed data (Users, Roles, Sections)
   - Oracle opportunities (from sync_manager)
   ↓
4. User starts backend: python -m backend.app.main
   ↓
5. FastAPI starts (backend/app/main.py):
   - Loads routers (auth, inbox, scoring)
   - Auto-syncs on startup
   ↓
6. User starts frontend: npm run dev
   ↓
7. Frontend calls backend APIs:
   - /api/auth/users
   - /api/inbox/unassigned
   - /api/scoring/{id}/latest
```

### **Data Flow**
```
Oracle CRM
    ↓ (API calls via oracle_service.py)
sync_manager.py
    ↓ (maps & saves)
PostgreSQL Database (models.py schema)
    ↓ (queries via routers)
FastAPI Endpoints
    ↓ (JSON responses)
React Frontend
```

### **Configuration Flow**
```
.env file
    ↓ (loaded by)
backend/app/services/oracle_service.py
backend/app/core/database.py
    ↓ (provides)
Database connection
Oracle API credentials
```

---

## 🚀 CLEANUP EXECUTION PLAN

### **Phase 1: Backup (Safety First)**
```bash
# Create a backup before deletion
mkdir BQS_BACKUP
xcopy /E /I /Y backend BQS_BACKUP\backend
xcopy /E /I /Y scripts BQS_BACKUP\scripts
xcopy *.py BQS_BACKUP\
xcopy *.md BQS_BACKUP\
```

### **Phase 2: Delete Root Clutter**
I'll create a script to safely delete all obsolete files.

### **Phase 3: Clean Backend**
Remove duplicate files from `backend/` directory.

### **Phase 4: Organize Scripts**
Move useful debugging scripts to `scripts/util/`.

### **Phase 5: Consolidate Documentation**
Merge all guides into a single comprehensive README.md.

---

## 📊 SUMMARY

| Category | Keep | Delete | Move |
|----------|------|--------|------|
| Root Python Scripts | 1 | 40+ | 5 |
| Backend Files | 1 folder (app/) | 15+ | 3 |
| Documentation | 2 | 14 | 1 |
| Scripts | 1 | 30+ | 5 |

**Total Files to Delete: ~100+**
**Final Clean Structure: ~30 essential files**

---

## ✅ NEXT STEPS

1. **Review this plan** - Make sure you're comfortable with deletions
2. **Run the cleanup script** - I'll create an automated script
3. **Test the application** - Ensure everything still works
4. **Commit to Git** - Save the clean structure

**Ready to proceed with automated cleanup?**
