# Dashboard Data Sync - Troubleshooting Guide

## Problem Statement
You have existing assessment data in `opp_score_version` table:
- 3 assessments submitted
- 2 APPROVED/ACCEPTED
- 1 REJECTED

These should appear in the Practice Head Dashboard but are not showing up.

## Root Cause
The `workflow_status` column was recently added to the `opportunity` table. Existing opportunities have NULL values in this column, so the dashboard filtering logic cannot categorize them correctly.

## Solution

### Step 1: Run the Migration Script
Execute the sync script to populate `workflow_status` from existing assessment data:

```bash
python backend\sync_workflow_status.py
```

This script:
1. Reads the latest `opp_score_version` status for each opportunity
2. Maps it to the appropriate `workflow_status`:
   - `SUBMITTED` → `SUBMITTED_FOR_REVIEW`
   - `DRAFT` → `UNDER_ASSESSMENT`
   - `APPROVED` → `APPROVED`
   - `REJECTED` → `REJECTED`
   - `ACCEPTED` → `ACCEPTED`
3. Updates the `opportunity` table

### Step 2: Verify the Data
Check the database directly:

```sql
-- See all opportunities with their workflow status
SELECT opp_id, opp_name, workflow_status 
FROM opportunity 
WHERE workflow_status IS NOT NULL;

-- Count by status
SELECT workflow_status, COUNT(*) 
FROM opportunity 
GROUP BY workflow_status;
```

### Step 3: Restart the Backend
After migration, restart your FastAPI server to ensure fresh data:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Step 4: Refresh the Dashboard
1. Open the Practice Head Dashboard
2. Navigate to the "Approved" tab - you should see 2 opportunities
3. Navigate to the "Rejected" tab - you should see 1 opportunity

## Expected Dashboard Distribution

**Practice Head Dashboard Tabs:**
- **Approved**: 2 opportunities (those with APPROVED/ACCEPTED status)
- **Rejected**: 1 opportunity (the one you rejected)
- **Under-Assessment**: Any with DRAFT status
- **Assigned to SA**: Any with ASSIGNED_TO_SA status
- **Unassigned**: Any without assignments

## Verification Checklist
- [ ] Migration script executed successfully
- [ ] Database shows correct `workflow_status` values
- [ ] Backend server restarted
- [ ] Frontend refreshed (hard refresh: Ctrl+Shift+R)
- [ ] Approved tab shows 2 items
- [ ] Rejected tab shows 1 item

## If Issues Persist

### Check API Response
Open browser DevTools → Network tab, then:
1. Refresh the dashboard
2. Find the request to `/api/opportunities`
3. Check the response - verify `workflow_status` field is populated

### Check Frontend Filtering
The filtering logic in `PracticeHeadDashboard.tsx` should match:
```typescript
case 'approved':
    filtered = filtered.filter(o => ['APPROVED', 'ACCEPTED', 'COMPLETED', 'WON'].includes(getStatus(o)));
    break;
case 'rejected':
    filtered = filtered.filter(o => getStatus(o) === 'REJECTED' || getStatus(o) === 'LOST');
    break;
```

### Manual Database Fix (if needed)
If the migration script fails, you can manually update:

```sql
-- For a specific opportunity
UPDATE opportunity 
SET workflow_status = 'APPROVED' 
WHERE opp_id = 'YOUR_OPP_ID';
```
