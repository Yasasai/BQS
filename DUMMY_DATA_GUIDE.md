# BQS Dummy Data Generation - Quick Start Guide

## ✅ What I've Done

I've updated your BQS system with the following:

### 1. **Database Schema Update** (`database.py`)
- Added `assigned_to` field to the `Opportunity` model
- This allows tracking which Solution Architect is assigned to each opportunity
- Field is nullable, so opportunities can be unassigned

### 2. **Dummy Data Generator Script** (`populate_dummy_data.py`)
- Creates **15 realistic opportunities** with:
  - ~40% **UNASSIGNED** (perfect for demonstrating assignment workflow)
  - ~60% **ASSIGNED** to Solution Architects (John Smith, Michael Chen, David Wilson)
  - Diverse customers, practices, geos, and sales stages
  - Deal values from $100K to $5M
  - Realistic dates and probabilities

- Creates **5 users**:
  - 3 Solution Architects
  - 1 Sales Manager
  - 1 Bid Manager

- Creates **~9 assessments** with:
  - Multiple versions (v1.0, v2.0, v3.0)
  - 8 scoring criteria
  - Automated verdicts (Strongly Recommended, Recommended, Conditional, Not Recommended)
  - Risk analysis (2-4 risks per assessment)
  - Mix of submitted and draft states

## 🚀 How to Run the Script

### Option 1: Using the Batch File
```cmd
cd backend
run_populate.bat
```

### Option 2: Direct Python Command
```cmd
cd backend
python populate_dummy_data.py
```

### Option 3: From Project Root
```cmd
python backend\populate_dummy_data.py
```

## 📊 What You'll See

The script will output:
```
============================================================
BQS DUMMY DATA GENERATOR
============================================================

Initializing database...
✓ Database initialized

Clearing existing data...
✓ Existing data cleared

Creating users...
✓ Created 5 users

Creating opportunities...
  Created opportunity 1/15: ...
  Created opportunity 2/15: ...
  ...
✓ Created 15 opportunities

Creating assessments...
✓ Created X assessments

============================================================
DUMMY DATA GENERATION SUMMARY
============================================================

📊 Total Opportunities: 15
📝 Total Assessments: ~15-20
👥 Total Users: 5

🎯 Opportunities by Stage:
   • Qualification: X
   • Needs Analysis: X
   • Proposal: X
   • Negotiation: X
   • Closed Won: X
   • Closed Lost: X

💼 Opportunities by Practice:
   • Cybersecurity: X
   • Cloud: X
   • Data & Analytics: X
   • AI & Machine Learning: X
   ...

👤 Assignment Status:
   • Assigned to Solution Architect: ~9
   • Unassigned (Needs Assignment): ~6

💰 Total Pipeline Value: $XX,XXX,XXX.XX

✅ Submitted Assessments: X
📝 Draft Assessments: X

============================================================
✓ Dummy data generation complete!
============================================================

🎉 Your database is now ready for the presentation!
```

## 🎯 Perfect for Your Meeting

This data showcases:
1. **Assignment Workflow** - Unassigned opportunities ready for the "Assign Solution Architect" modal
2. **Pipeline Diversity** - Multiple industries, practices, and geos
3. **Assessment Lifecycle** - Draft and submitted assessments with versions
4. **Risk Management** - Comprehensive risk tracking
5. **Decision Support** - Automated scoring and verdicts

## ⚠️ Troubleshooting

If the script hangs or doesn't run:

1. **Check PostgreSQL is running**:
   ```cmd
   pg_isready -h 127.0.0.1 -p 5432
   ```

2. **Verify database connection**:
   - Host: 127.0.0.1
   - Port: 5432
   - Database: bqs
   - User: postgres
   - Password: Abcd1234

3. **Test database import**:
   ```cmd
   python -c "from database import init_db; init_db(); print('Success!')"
   ```

4. **Run with error output**:
   ```cmd
   python populate_dummy_data.py 2>&1 | more
   ```

## 📝 Next Steps After Population

1. **Start Backend**:
   ```cmd
   cd backend
   python main.py
   ```

2. **Start Frontend** (in new terminal):
   ```cmd
   cd frontend
   npm run dev
   ```

3. **View in Browser**:
   ```
   http://localhost:5173
   ```

## 📂 Files Created/Modified

- ✅ `backend/database.py` - Added `assigned_to` field
- ✅ `backend/populate_dummy_data.py` - Dummy data generator
- ✅ `backend/run_populate.bat` - Quick run script

---

**Ready for your meeting!** 🎉

The dummy data includes everything you need to demonstrate:
- Opportunity management
- Assignment workflow
- Assessment scoring
- Risk tracking
- Decision support
