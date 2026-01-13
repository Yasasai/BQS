# GitHub Push Checklist (BQS Professional)

To ensure your project is clean, secure, and ready for GitHub, please follow this checklist.

## 🛑 DO NOT PUSH (Sensitive/Temporary)
- `.env` (Your Oracle & DB Credentials) - **Git should ignore this automatically.**
- `__pycache__/` (Python internal files)
- `node_modules/` (Frontend libraries)
- `*.pyc`
- `final_status.txt`, `sync_output.txt`, etc. (Temporary debug logs)

## ✅ IMPORTANT FILES TO PUSH
### 1. Core Logic
- `backend/` (All `.py` files: main, database, sync_manager, oracle_service)
- `backend/requirements.txt` (Critical for setup)
- `frontend/` (Source files: src, public, index.html)
- `frontend/package.json` & `frontend/package-lock.json`

### 2. The Systematic Sync Engine
- `refined_sync_script.py` (The main manual/targeted sync tool)
- `standardize_env.py` (Tool to help others set up their .env)

### 3. Documentation
- `README.md` (Project overview)
- `ORACLE_SYNC_GUIDE.md` (How the sync works)
- `WALKTHROUGH.md` (Deep dive into self-healing)

### 4. Configuration
- `.gitignore` (The most important security file)
- `.agent/` (Your AI instructions/workflows)

## 🚀 Final Steps Before Push
1. Run `python standardize_env.py` to ensure your `.env` is standardized locally.
2. Ensure `load_dotenv()` uses absolute paths (Already implemented in `refined_sync_script.py`).
3. Verify that `remote_id` in PostgreSQL is mapped correctly to `OptyNumber`.

**Command to check what Git is seeing:**
```bash
git status
```
*If you see `.env` in the list of files to be committed, STOP and update your `.gitignore` immediately.*
