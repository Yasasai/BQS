# ✅ Oracle Sync - Fetch All Global Opportunities

## Change Applied

Updated the sync to fetch ALL global opportunities by removing the `q` parameter filter.

---

## What Changed

### **File:** `backend/app/services/sync_manager.py`

### **Before:**
```python
url = (
    f"{endpoint}"
    f"?q=RecordSet='ALL'"  # Still filtered
    f"&onlyData=true"
    f"&limit={limit}"
    f"&offset={offset}"
    f"&fields=..."
)
```

### **After:**
```python
url = (
    f"{endpoint}"
    f"?onlyData=true"  # No q parameter - fetch ALL
    f"&limit={limit}"
    f"&offset={offset}"
    f"&fields=OptyId,OptyNumber,Name,Revenue,WinProb,SalesStage,TargetPartyName,Practice_c,GEO_c,CurrencyCode,EffectiveDate,LastUpdateDate"
)
```

---

## Key Difference

| Parameter | Before | After |
|-----------|--------|-------|
| `q=RecordSet='ALL'` | ✅ Present | ❌ Removed |
| **Result** | 1 opportunity (yours) | ALL global opportunities |

---

## Why This Works

**Removing the `q` parameter:**
- Lets Oracle use its default view
- No ownership filter applied
- Returns all opportunities in the system
- Simplest and most reliable approach

---

## Test Now

### **1. Restart Backend:**
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python -m backend.app.main
```

### **2. Expected Output:**
```
🚀 BQS Starting...
🚀 Starting CLEAN Dynamic Sync...
📡 Fetching: Offset 0, Limit 50
🔗 Requesting: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities?onlyData=true&limit=50&offset=0&fields=...
   Processing 50 items...
   ✓ Saved: Opportunity 1
   ✓ Saved: Opportunity 2
   ✓ Saved: Opportunity 3
   ...
   ✓ Saved: Opportunity 50
📡 Fetching: Offset 50, Limit 50
   Processing 50 items...
   ...
🎉 Sync Complete! Total Saved: 150+ opportunities
```

### **3. Verify URL in Logs:**
```
🔗 Requesting: ...?onlyData=true&limit=50&offset=0&fields=...
```

**Should NOT see:** `q=RecordSet='ALL'`

---

## Verification

### **Check Database:**
```bash
psql -U postgres -d bqs
```

```sql
-- Check total count (should be much higher)
SELECT COUNT(*) FROM opportunities;

-- Check distinct owners
SELECT DISTINCT sales_owner FROM opportunities;

-- View sample data
SELECT opp_number, opp_name, sales_owner 
FROM opportunities 
LIMIT 20;
```

### **Check Frontend:**
```
http://localhost:5173
```
- Should show many more opportunities
- Should include opportunities from different users
- Metrics should reflect global data

---

## If This Doesn't Work

Try **Option 2: PrimaryKey Finder**

Update line 107 to:
```python
f"?finder=PrimaryKey&onlyData=true"
```

Or **Option 3: Contact Oracle Admin**
- Ask for the correct finder name to fetch all opportunities
- Verify API user has permissions to view all opportunities

---

## Summary

**Change:** Removed `q=RecordSet='ALL'` parameter
**File:** `backend/app/services/sync_manager.py`
**Line:** 107
**Result:** Should fetch ALL global opportunities

---

## Next Steps

1. **Restart backend** → See new URL without q parameter
2. **Watch logs** → Should fetch many more opportunities
3. **Check database** → Should have opportunities from all users
4. **Verify frontend** → Should show global data

---

**You should now see ALL global opportunities from Oracle CRM!** 🌍
