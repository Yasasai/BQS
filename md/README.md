# BQS - Bid Qualification System

Oracle CRM to PostgreSQL synchronization system with FastAPI backend and React frontend.

## Features

- 🔄 **Automated Oracle CRM Sync** - Daily scheduled synchronization
- 🗄️ **Self-Healing Database** - Automatic schema migrations
- 🌐 **REST API** - FastAPI backend with comprehensive endpoints
- 🔍 **Multiple Sync Methods**:
  - REST API sync (for users with API access)
  - UI Scraper (Selenium-based for restricted accounts)
  - Name-based fetching (for specific opportunities)
- 📊 **Comprehensive Data Capture** - Stores full opportunity details and raw JSON

## Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd BQS
```

### 2. Create `.env` File
Create a `.env` file in the root directory:
```env
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
DATABASE_URL=postgresql://postgres:your_db_password@127.0.0.1:5432/bqs
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Backend
```bash
python backend/main.py
```

The server will start at `http://localhost:8000`

## Sync Methods

### Method 1: Automated API Sync (Recommended if you have API access)
The backend automatically syncs daily at midnight. To trigger manually:
```bash
curl -X POST http://localhost:8000/api/sync-database
```

Or run the script:
```bash
python refined_sync_script.py
```

### Method 2: UI Scraper (For restricted API access)
Uses Selenium to scrape the Oracle UI:
```bash
python scripts/scrape_oracle_ui.py
```

**Prerequisites**: Chrome browser installed

### Method 3: Fetch by Names
If you know specific opportunity names:
```bash
python fetch_by_names.py
```

Edit the script to add opportunity names from your dashboard.

## Project Structure

```
BQS/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── oracle_service.py    # Oracle API integration
│   └── sync_manager.py      # Sync orchestration
├── scripts/
│   └── scrape_oracle_ui.py  # Selenium UI scraper
├── frontend/                # React application
├── refined_sync_script.py   # Manual sync script
├── fetch_by_names.py        # Name-based fetcher
├── verify_details.py        # Data verification tool
├── requirements.txt         # Python dependencies
└── .env                     # Configuration (create locally)
```

## API Endpoints

- `GET /api/opportunities` - List all opportunities
- `GET /api/oracle-opportunity/{id}` - Get single opportunity with details
- `POST /api/sync-database` - Trigger manual sync
- `GET /api/sync-status` - Get last sync status
- `GET /api/sync-history` - View sync history

## Database Schema

### `opportunities` Table
Primary opportunity data from Oracle CRM

### `opportunity_details` Table
Extended details including:
- Owner and contact information
- Financial details
- Raw JSON from Oracle API (for auditing)

### `sync_logs` Table
Tracks all sync operations with statistics

## Troubleshooting

### "0 opportunities synced"
- **Cause**: User doesn't have REST API access
- **Solution**: Use the UI scraper (`scripts/scrape_oracle_ui.py`)

### "404 Not Found" on API calls
- **Cause**: Incorrect API version
- **Solution**: Check Oracle admin for correct API endpoint

### Database connection errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database `bqs` exists

## Development

### Run Tests
```bash
python verify_details.py
```

### View Logs
Check console output when running `backend/main.py`

## Security

- Never commit `.env` file (already in `.gitignore`)
- Credentials are loaded from environment variables only
- No hardcoded passwords in source code

## License

Internal use only - Inspira Enterprise

## Support

Contact the development team for issues or questions.
