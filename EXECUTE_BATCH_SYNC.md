# 🚀 Execute Batch Sync - Quick Guide

## Updated URL Format

The batch sync now uses the EXACT URL format you specified:

```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
&fields=OpportunityId,OpportunityNumber
&limit=5
&offset=0
```

## Changes Made

### 1. Removed Parameters:
- ❌ `q=RecordSet='ALL'` (removed)
- ❌ `onlyData=true` (removed)

### 2. Updated Field Names:
- ✅ `OpportunityId` (was `OptyId`)
- ✅ `OpportunityNumber` (was `OptyNumber`)

### 3. Kept Parameters:
- ✅ `finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'`
- ✅ `fields=OpportunityId,OpportunityNumber`
- ✅ `limit=5` (configurable)
- ✅ `offset=0` (auto-increments)

## Execute Now

### Command:
```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python batch_sync_with_offset.py
```

### Expected Output:
```
======================================================================
🚀 Starting Batch Sync with Offset Tracking
======================================================================
📝 Created new sync state for 'oracle_opportunities'

======================================================================
📦 Batch: Offset=0, Size=5
======================================================================
🔗 Built URL: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&fields=OpportunityId,OpportunityNumber&limit=5&offset=0
📡 Calling API: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi...
✅ Received 5 items
📝 Processing 5 items...
   ✅ Saved: 300000001234567 - 1902737
   ✅ Saved: 300000001234568 - 1672704
   ✅ Saved: 300000001234569 - 1673697
   ✅ Saved: 300000001234570 - 1902738
   ✅ Saved: 300000001234571 - 1658758
✅ Batch complete: 5/5 saved
💾 Updated offset to 5, total synced: 5

======================================================================
📦 Batch: Offset=5, Size=5
======================================================================
🔗 Built URL: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&fields=OpportunityId,OpportunityNumber&limit=5&offset=5
📡 Calling API: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi...
✅ Received 5 items
📝 Processing 5 items...
   ✅ Saved: 300000001234572 - 1658759
   ...

🎉 Sync Complete!
   Total Synced: 150
   Final Offset: 150
======================================================================
```

## Verify After Execution

### Check Database:
```bash
psql -U postgres -d bqs
```

```sql
-- Check sync state
SELECT * FROM sync_state;

-- Check synced opportunities
SELECT COUNT(*) FROM minimal_opportunities;

-- View sample data
SELECT * FROM minimal_opportunities LIMIT 10;
```

### Check Status:
```bash
python batch_sync_with_offset.py status
```

## URL Examples

### First Batch (offset=0):
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&fields=OpportunityId,OpportunityNumber&limit=5&offset=0
```

### Second Batch (offset=5):
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&fields=OpportunityId,OpportunityNumber&limit=5&offset=5
```

### Third Batch (offset=10):
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'&fields=OpportunityId,OpportunityNumber&limit=5&offset=10
```

## Ready to Execute!

The file `batch_sync_with_offset.py` is now updated with your exact URL format.

Run it with:
```bash
python batch_sync_with_offset.py
```
