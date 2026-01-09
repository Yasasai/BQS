# BQS Dashboards - Indestructible Setup

This project is designed with a **Self-Healing Architecture**. If you accidentally delete your database, your folders, or your environment, you can bring it back to 100% capacity in seconds.

## 🚀 The Self-Heal Protocol
If anything goes wrong (db errors, missing files, fresh clone), simply run:
```bash
python self_heal.py
```
This script will:
1. Re-install all backend and frontend dependencies.
2. Re-create the PostgreSQL database and tables.
3. **Restore all your data** (opportunities, assessments, users) from the `database_dump.json`.

---

## 🛡️ GitHub Resilience (How to Push/Pull safely)

The most common reason for "losing progress" is not backing up the database before a push. Follow these 3 steps every day:

### 1. BEFORE YOU PUSH (Backup)
Always export your current database data to the JS0N file so it goes to GitHub:
```bash
cd backend
venv\Scripts\activate
python dump_data.py
```
*This updates `database_dump.json` in the root.*

### 2. COMMIT & PUSH
```bash
git add .
git commit -m "feat: your changes"
git push
```

### 3. AFTER YOU CLONE / PULL (Self-Heal)
If you move to another machine or lose data after a pull:
```bash
python self_heal.py
```

---

## 📂 Project Structure
- `backend/`: FastAPI application, Database models, and Backup/Restore scripts.
- `frontend/`: Vite + React + Tailwind CSS dashboard.
- `database_dump.json`: **The master heartbeat of your progress.** Do not delete this; it contains your actual data.

## 🛠️ Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL (running locally with password `Abcd1234`)

## 🚦 Starting the App
- **Backend**: `cd backend && python main.py` (Port 8000)
- **Frontend**: `cd frontend && npm run dev` (Port 5173)
