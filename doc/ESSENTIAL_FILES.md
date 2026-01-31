# 🎯 The 30 Essential Files - Complete List

## Overview
After cleanup, your BQS project will have **exactly these 30 essential files** (excluding frontend, which has its own structure, and the venv folder).

---

## 📁 **ROOT DIRECTORY (5 files)**

```
BQS/
├── .env                          # 1️⃣  Environment variables (Oracle credentials, DB URL)
├── .gitignore                    # 2️⃣  Git exclusions
├── README.md                     # 3️⃣  Main project documentation
├── fix_install.py                # 4️⃣  Quick dependency installer
└── cleanup_project.py            # 5️⃣  Cleanup automation script
```

**Purpose:**
- `.env` - Stores all sensitive configuration
- `.gitignore` - Prevents committing secrets/temp files
- `README.md` - First thing developers read
- `fix_install.py` - Fixes dependency issues quickly
- `cleanup_project.py` - Removes duplicate files

---

## 📁 **BACKEND STRUCTURE (13 files)**

### **Backend Root (2 files)**
```
backend/
├── requirements.txt              # 6️⃣  Python dependencies
└── __init__.py                   # 7️⃣  Package marker
```

### **Backend App (11 files)**
```
backend/app/
├── __init__.py                   # 8️⃣  Package marker
├── main.py                       # 9️⃣  FastAPI entry point
├── models.py                     # 🔟  Database models (all tables)
│
├── core/
│   ├── __init__.py               # 1️⃣1️⃣  Package marker
│   ├── database.py               # 1️⃣2️⃣  DB connection & initialization
│   └── constants.py              # 1️⃣3️⃣  Shared enums & constants
│
├── routers/
│   ├── __init__.py               # 1️⃣4️⃣  Package marker
│   ├── auth.py                   # 1️⃣5️⃣  User authentication APIs
│   ├── inbox.py                  # 1️⃣6️⃣  Opportunity inbox APIs
│   └── scoring.py                # 1️⃣7️⃣  Assessment scoring APIs
│
└── services/
    ├── __init__.py               # 1️⃣8️⃣  Package marker
    ├── oracle_service.py         # 1️⃣9️⃣  Oracle CRM API integration
    └── sync_manager.py           # 2️⃣0️⃣  Data synchronization logic
```

**Purpose:**
- `main.py` - Starts the FastAPI server
- `models.py` - Defines all database tables
- `core/database.py` - Handles DB connection
- `core/constants.py` - Shared values used everywhere
- `routers/*.py` - API endpoints for frontend
- `services/oracle_service.py` - Talks to Oracle CRM
- `services/sync_manager.py` - Syncs Oracle data to DB

---

## 📁 **SCRIPTS (2 files)**

```
scripts/
├── setup/
│   └── setup_project.py          # 2️⃣1️⃣  Universal setup script
└── util/
    └── (debugging tools)         # 2️⃣2️⃣  Optional utilities (moved from root)
```

**Purpose:**
- `setup_project.py` - One command to set up everything
- `util/` - Debugging scripts (optional, can be empty)

---

## 📁 **DOCUMENTATION (3 files)**

```
doc/
├── ARCHITECTURE.md               # 2️⃣3️⃣  System architecture & diagrams
├── PROJECT_CLEANUP_PLAN.md       # 2️⃣4️⃣  Cleanup plan & file lists
└── CLEANUP_SUMMARY.md            # 2️⃣5️⃣  Quick reference guide
```

**Purpose:**
- `ARCHITECTURE.md` - How everything works together
- `PROJECT_CLEANUP_PLAN.md` - What to delete and why
- `CLEANUP_SUMMARY.md` - Quick overview

---

## 📁 **FRONTEND (5 key files + src/)**

```
frontend/
├── package.json                  # 2️⃣6️⃣  Node dependencies
├── package-lock.json             # 2️⃣7️⃣  Dependency lock file
├── vite.config.ts                # 2️⃣8️⃣  Build configuration
├── tsconfig.json                 # 2️⃣9️⃣  TypeScript configuration
├── index.html                    # 3️⃣0️⃣  Entry HTML
└── src/                          # React components (many files)
    ├── main.tsx
    ├── App.tsx
    └── components/
```

**Purpose:**
- Frontend is its own ecosystem with React components
- These 5 files are the configuration layer
- `src/` contains all your React code

---

## 📊 **The 30 Essential Files Breakdown**

| Category | Count | Files |
|----------|-------|-------|
| **Root Config** | 5 | .env, .gitignore, README.md, fix_install.py, cleanup_project.py |
| **Backend Core** | 13 | requirements.txt, __init__.py files, main.py, models.py, core/, routers/, services/ |
| **Scripts** | 2 | setup_project.py, util/ |
| **Documentation** | 3 | ARCHITECTURE.md, PROJECT_CLEANUP_PLAN.md, CLEANUP_SUMMARY.md |
| **Frontend Config** | 5 | package.json, vite.config.ts, tsconfig.json, index.html, package-lock.json |
| **Frontend Source** | ∞ | src/ folder (your React components) |
| **TOTAL** | **30** | **(excluding frontend/src/ and venv/)** |

---

## 🔍 **Detailed Purpose of Each File**

### **Configuration (5 files)**
1. `.env` - Oracle credentials, database URL
2. `.gitignore` - Don't commit venv/, __pycache__, .env
3. `requirements.txt` - fastapi, sqlalchemy, psycopg2, etc.
4. `package.json` - React, TypeScript, Vite dependencies
5. `vite.config.ts` - Frontend build settings

### **Application Entry Points (2 files)**
6. `backend/app/main.py` - FastAPI server
7. `frontend/index.html` - React app entry

### **Database Layer (2 files)**
8. `backend/app/models.py` - Table schemas
9. `backend/app/core/database.py` - Connection & init

### **API Layer (3 files)**
10. `backend/app/routers/auth.py` - User APIs
11. `backend/app/routers/inbox.py` - Opportunity APIs
12. `backend/app/routers/scoring.py` - Assessment APIs

### **Business Logic (2 files)**
13. `backend/app/services/oracle_service.py` - Oracle integration
14. `backend/app/services/sync_manager.py` - Data sync

### **Utilities (3 files)**
15. `backend/app/core/constants.py` - Shared enums
16. `scripts/setup/setup_project.py` - Setup automation
17. `fix_install.py` - Dependency fixer

### **Documentation (3 files)**
18. `README.md` - Project overview
19. `doc/ARCHITECTURE.md` - System design
20. `doc/PROJECT_CLEANUP_PLAN.md` - Cleanup guide

### **Package Markers (5 files)**
21-25. `__init__.py` files - Make Python packages importable

### **Cleanup Tools (2 files)**
26. `cleanup_project.py` - Automated cleanup
27. `doc/CLEANUP_SUMMARY.md` - Cleanup summary

### **Frontend Config (3 files)**
28. `tsconfig.json` - TypeScript settings
29. `package-lock.json` - Exact dependency versions
30. `frontend/src/` - All React components

---

## 🎯 **Why Only 30?**

### **Before Cleanup:**
- 150+ files scattered everywhere
- Duplicates: 3 versions of database.py, 5 sync scripts, 10+ setup scripts
- Confusion: Which file does what?
- Hard to maintain

### **After Cleanup:**
- 30 essential files (+ frontend/src/)
- Each file has ONE clear purpose
- No duplicates
- Easy to understand and maintain

---

## ✅ **What About Frontend/src/?**

The `frontend/src/` folder contains your React components. This can have many files:
```
frontend/src/
├── main.tsx
├── App.tsx
├── components/
│   ├── Dashboard.tsx
│   ├── OpportunityInbox.tsx
│   ├── AssessmentForm.tsx
│   └── ... (your UI components)
├── services/
│   └── api.ts
└── styles/
    └── index.css
```

**These are NOT counted in the "30 essential files"** because:
- Frontend is its own ecosystem
- Number of components varies by features
- They're all in one organized folder

---

## 🚀 **The Bottom Line**

**30 Essential Backend/Config Files:**
- 5 in root (config)
- 13 in backend (application)
- 2 in scripts (setup)
- 3 in doc (documentation)
- 5 in frontend root (config)
- 2 cleanup tools

**Plus:**
- `frontend/src/` - Your React components (variable count)
- `backend/venv/` - Virtual environment (auto-generated)
- `.git/` - Git repository (auto-managed)

**Total visible files you'll work with: ~30-40**

**Total files before cleanup: 150+**

**Reduction: ~75% fewer files to manage! 🎉**

---

## 📋 **Quick Reference: Which File for What?**

| I want to... | Edit this file |
|--------------|----------------|
| Change database schema | `backend/app/models.py` |
| Add new API endpoint | `backend/app/routers/*.py` |
| Change Oracle sync logic | `backend/app/services/sync_manager.py` |
| Update Oracle API calls | `backend/app/services/oracle_service.py` |
| Change database connection | `backend/app/core/database.py` |
| Add shared constants | `backend/app/core/constants.py` |
| Update credentials | `.env` |
| Add Python dependency | `backend/requirements.txt` |
| Add frontend dependency | `frontend/package.json` |
| Change UI | `frontend/src/components/*.tsx` |
| Update setup process | `scripts/setup/setup_project.py` |
| Understand architecture | `doc/ARCHITECTURE.md` |

**That's it! Just 30 essential files to know.** 🎯
