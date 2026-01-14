# BQS Project - GitHub Push Checklist

## ✅ Pre-Push Checklist

### 1. Clean Up Temporary Files
Run this command to remove test/diagnostic scripts:
```bash
del test_oracle_permissions.py
del test_oracle_data.py
del direct_api_test.py
del diagnose_sync.py
del quick_verify_fix.py
del find_oracle_url.py
del fetch_all_methods.py
del extract_names.py
del api_test.txt
del sync_output_*.txt
del oracle_api_config.txt
del opportunity_names.txt
del fetched_opportunities.json
```

### 2. Verify Core Files Are Present
Ensure these essential files exist:
- ✅ `backend/main.py` - FastAPI server
- ✅ `backend/database.py` - Database models
- ✅ `backend/oracle_service.py` - Oracle API integration
- ✅ `backend/sync_manager.py` - Sync orchestration
- ✅ `refined_sync_script.py` - Manual sync script
- ✅ `verify_details.py` - Data verification
- ✅ `scripts/scrape_oracle_ui.py` - Selenium scraper
- ✅ `fetch_by_names.py` - Fetch by opportunity names
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Excludes secrets and temp files
- ✅ `README.md` - Project documentation

### 3. Remove Hardcoded Credentials
**CRITICAL**: Before pushing, remove hardcoded credentials from:

#### `refined_sync_script.py` - Lines 8-13
Replace:
```python
os.environ["ORACLE_USER"] = "yasasvi.upadrasta@inspiraenterprise.com"
os.environ["ORACLE_PASSWORD"] = "Welcome@123"
```
With:
```python
# Load from .env file (create .env locally with your credentials)
from dotenv import load_dotenv
load_dotenv()
os.environ["ORACLE_USER"] = os.getenv("ORACLE_USER", "")
os.environ["ORACLE_PASSWORD"] = os.getenv("ORACLE_PASSWORD", "")
```

#### `scripts/scrape_oracle_ui.py` - Lines 16-17
Replace:
```python
ORACLE_USER = "yasasvi.upadrasta@inspiraenterprise.com"
ORACLE_PASS = "Welcome@123"
```
With:
```python
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASS = os.getenv("ORACLE_PASSWORD", "")
```

#### `fetch_by_names.py` - Lines 13-14
Replace hardcoded credentials with:
```python
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASS = os.getenv("ORACLE_PASSWORD", "")
```

### 4. Update README.md
Add setup instructions for collaborators:
```markdown
## Setup Instructions

1. Clone the repository
2. Create a `.env` file in the root directory:
   ```
   ORACLE_USER=your_username
   ORACLE_PASSWORD=your_password
   ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
   DATABASE_URL=postgresql://postgres:your_password@127.0.0.1:5432/bqs
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run the backend: `python backend/main.py`
```

### 5. Verify .gitignore
Ensure `.env` is in `.gitignore` (already done ✅)

### 6. Git Commands
```bash
# Check what will be committed
git status

# Add all files
git add .

# Commit with meaningful message
git commit -m "feat: Complete Oracle CRM sync with UI scraper and name-based fetching"

# Push to GitHub
git push origin main
```

## 📦 What Will Be Pushed

### Core Backend
- `backend/main.py` - FastAPI application with self-healing DB
- `backend/database.py` - Models: Opportunity, OpportunityDetails, SyncLog
- `backend/oracle_service.py` - Oracle REST API integration
- `backend/sync_manager.py` - Automated sync orchestration

### Sync Scripts
- `refined_sync_script.py` - Manual full/incremental sync
- `fetch_by_names.py` - Fetch opportunities by name (for API limitations)
- `scripts/scrape_oracle_ui.py` - Selenium-based UI scraper

### Utilities
- `verify_details.py` - Database verification tool
- `requirements.txt` - All Python dependencies

### Documentation
- `README.md` - Project overview and setup
- `.gitignore` - Excludes secrets and temp files

## ⚠️ What Will NOT Be Pushed (Protected by .gitignore)
- `.env` - Your credentials (SAFE ✅)
- `__pycache__/` - Python cache
- `node_modules/` - Frontend dependencies
- `*.log` - Log files
- Test/diagnostic scripts (deleted in step 1)

## 🔒 Security Check
Before pushing, verify:
```bash
# Search for any remaining hardcoded passwords
findstr /s /i "Welcome@123" *.py
findstr /s /i "yasasvi.upadrasta" *.py
```

If any results appear, remove them!

## ✅ Final Verification
1. Run the backend: `python backend/main.py` (should start without errors)
2. Run verification: `python verify_details.py` (should show DB status)
3. Check git status: `git status` (should not show .env)

## 🚀 Ready to Push!
Once all checks pass, run:
```bash
git push origin main
```
