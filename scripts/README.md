# BQS Scripts Directory

This directory contains utility scripts for database management and maintenance.

## Available Scripts

### `db_manager.py` - Database Management (Main Script)

**Consolidated script for all database operations:**

```bash
# Self-heal database schema (add missing columns)
python scripts/db_manager.py heal

# Populate test data (7 opportunities covering all workflow stages)
python scripts/db_manager.py populate

# Check database status
python scripts/db_manager.py check

# Reset database (heal + populate)
python scripts/db_manager.py reset
```

## Quick Start

**First time setup:**
```bash
python scripts/db_manager.py reset
```

This will:
1. ✅ Add any missing columns to the database
2. ✅ Populate 7 test opportunities
3. ✅ Verify the data

## Test Data Included

After running `populate`, you'll have:

| Status | Count | Purpose |
|--------|-------|---------|
| NEW_FROM_CRM | 1 | Test Management assignment |
| ASSIGNED_TO_PRACTICE | 1 | Test PH assignment to SA |
| ASSIGNED_TO_SA | 1 | Test SA scoring |
| **WAITING_PH_APPROVAL** | **2** | **Test PH Accept/Reject** ⭐ |
| **READY_FOR_MGMT_REVIEW** | **2** | **Test Mgmt GO/NO-GO** ⭐ |

## Troubleshooting

**Database connection error:**
- Check PostgreSQL is running
- Verify credentials in `db_manager.py` (default: postgres/Abcd1234)

**Column errors:**
- Run: `python scripts/db_manager.py heal`

**No data showing:**
- Run: `python scripts/db_manager.py populate`
