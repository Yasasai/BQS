# BQS - Bid Qualification System

**Professional workflow management system for bid qualification with Oracle CRM integration.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)](https://www.postgresql.org/)

---

## 🚀 Quick Start (For Anyone)

**Clone and run in 3 commands:**

```bash
git clone <your-repo-url>
cd BQS
python scripts/setup_project.py --with-data
```

That's it! The script handles everything:
- ✅ Creates virtual environment
- ✅ Installs all dependencies (Python + Node.js)
- ✅ Sets up PostgreSQL database
- ✅ Populates test data
- ✅ Ready to run!

---

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 14+**

---

## 🏗️ Project Structure

```
BQS/
├── backend/                 # FastAPI backend
│   ├── main.py             # API server (auto-heals on startup)
│   ├── database.py         # Database models
│   ├── constants.py        # Shared enums (no magic strings!)
│   ├── requirements.txt    # Python dependencies
│   └── venv/               # Virtual environment (gitignored)
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Dashboard pages
│   │   ├── components/     # Reusable components
│   │   └── types.ts        # TypeScript types
│   ├── package.json
│   └── node_modules/       # (gitignored)
│
├── scripts/                # Utility scripts
│   ├── setup_project.py    # 🌟 Universal setup (run this first!)
│   ├── db_manager.py       # Database management
│   └── sync_oracle_master.py  # Oracle CRM sync
│
└── .gitignore              # Professional git hygiene
```

---

## 🎯 Running the Application

### Option 1: Automated Setup (Recommended)

```bash
# Complete setup + test data
python scripts/setup_project.py --with-data

# Then start the servers:
# Terminal 1 - Backend
cd backend
venv\Scripts\python main.py  # Windows
# venv/bin/python main.py    # Mac/Linux

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Open:** http://localhost:5173

---

## 🔧 Database Management

### Self-Healing Database

The backend **automatically heals** the database schema on startup:
- Detects missing columns
- Adds them without data loss
- Never breaks on schema changes

### Manual Database Commands

```bash
# Check database status
python scripts/db_manager.py check

# Fix schema issues
python scripts/db_manager.py heal

# Populate test data
python scripts/db_manager.py populate

# Reset everything (heal + populate)
python scripts/db_manager.py reset
```

---

## 🔄 Oracle CRM Synchronization

### Self-Healing Sync

The sync script uses **UPSERT logic** (INSERT ... ON CONFLICT DO UPDATE):
- ✅ Updates existing opportunities
- ✅ Inserts new opportunities
- ✅ No duplicate errors
- ✅ Can run every 5 minutes safely

```bash
# Sync from Oracle CRM
python scripts/sync_oracle_master.py

# Sync + mark stale records
python scripts/sync_oracle_master.py --clean
```

### Configuration

Set these environment variables (or edit `scripts/sync_oracle_master.py`):

```bash
ORACLE_BASE_URL=https://your-oracle-instance.com
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password
```

---

## 📊 Workflow Stages

| Status | Description | Who Acts |
|--------|-------------|----------|
| `NEW_FROM_CRM` | Fresh from Oracle | Management |
| `ASSIGNED_TO_PRACTICE` | Practice assigned | Practice Head |
| `ASSIGNED_TO_SA` | SA working on it | Solution Architect |
| `WAITING_PH_APPROVAL` | Awaiting PH review | Practice Head |
| `READY_FOR_MGMT_REVIEW` | Ready for final decision | Management |
| `COMPLETED_BID` | Approved (GO) | - |
| `COMPLETED_NO_BID` | Rejected (NO-GO) | - |

---

## 🎨 Features

### ✅ Self-Healing Architecture
- **Database**: Auto-adds missing columns on startup
- **Oracle Sync**: UPSERT logic prevents duplicates
- **Error Recovery**: Graceful handling of failures

### ✅ Role-Based Workflow
- **Management**: Assign to practice, final GO/NO-GO
- **Practice Head**: Assign to SA, Accept/Reject scores
- **Solution Architect**: Score opportunities, submit for review

### ✅ Professional Git Hygiene
- Clean `.gitignore` (no secrets, no temp files)
- Only source code goes to GitHub
- Safe to run `git add .` anytime

### ✅ No Magic Strings
- All statuses defined in `backend/constants.py`
- Shared between frontend and backend
- Type-safe, autocomplete-friendly

---

## 🧪 Test Data

After running `python scripts/db_manager.py populate`, you'll have:

| Opportunity | Status | Purpose |
|-------------|--------|---------|
| Enterprise Cloud Platform | NEW_FROM_CRM | Test Management assignment |
| Security Assessment | ASSIGNED_TO_PRACTICE | Test PH → SA assignment |
| Data Analytics Platform | ASSIGNED_TO_SA | Test SA scoring |
| **Deal Z - Cloud Migration** | **WAITING_PH_APPROVAL** | **Test PH Accept/Reject** ⭐ |
| **ERP Implementation** | **WAITING_PH_APPROVAL** | **Test PH Accept/Reject** ⭐ |
| **Cybersecurity Transformation** | **READY_FOR_MGMT_REVIEW** | **Test Mgmt GO/NO-GO** ⭐ |
| **Digital Transformation** | **READY_FOR_MGMT_REVIEW** | **Test Mgmt GO/NO-GO** ⭐ |

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
# Default connection: postgres:Abcd1234@localhost:5432/bqs

# Test connection
python -c "import psycopg2; psycopg2.connect('dbname=bqs user=postgres password=Abcd1234')"
```

### Schema errors
```bash
# Auto-heal the schema
python scripts/db_manager.py heal

# Or just restart backend (auto-heals on startup)
cd backend
venv\Scripts\python main.py
```

### No data showing
```bash
# Populate test data
python scripts/db_manager.py populate

# Or sync from Oracle
python scripts/sync_oracle_master.py
```

### Frontend won't connect
- Ensure backend is running on http://localhost:8000
- Check CORS settings in `backend/main.py`
- Verify frontend is on http://localhost:5173

---

## 📦 Deployment

### Environment Variables

Create `.env` file in `backend/`:

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
ORACLE_BASE_URL=https://your-oracle-instance.com
ORACLE_USERNAME=your_username
ORACLE_PASSWORD=your_password
```

### Production Checklist

- [ ] Set environment variables
- [ ] Update CORS origins in `backend/main.py`
- [ ] Configure PostgreSQL for production
- [ ] Set up Oracle CRM credentials
- [ ] Schedule `sync_oracle_master.py` (cron/scheduler)
- [ ] Build frontend: `npm run build`
- [ ] Deploy backend with gunicorn/uvicorn

---

## 🤝 Contributing

1. Clone the repository
2. Run `python scripts/setup_project.py --with-data`
3. Make your changes
4. Test thoroughly
5. Commit and push (`.gitignore` keeps it clean!)

---

## 📝 License

Proprietary - Internal Use Only

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `scripts/README.md` for detailed script documentation
3. Contact the development team

---

**Built with ❤️ for efficient bid qualification**
