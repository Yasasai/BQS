# 📦 Batch Sync with Offset Tracking - Documentation

## Overview
This is a **NEW, SEPARATE** sync implementation that does NOT mix with existing code. It implements your pseudocode exactly with offset tracking and resumable sync.

---

## 🆕 **What I Created**

### **New File:** `batch_sync_with_offset.py`

**Location:** `c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\batch_sync_with_offset.py`

**Purpose:** Standalone batch sync with offset tracking

**Does NOT affect:**
- ❌ `backend/app/services/sync_manager.py` (untouched)
- ❌ `backend/app/main.py` (untouched)
- ❌ Existing `opportunities` table (untouched)

---

## 📊 **New Database Tables**

### **1. `sync_state` Table**
Tracks sync progress for resumable sync

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer | Primary key |
| `sync_name` | String | Name of sync job (e.g., "oracle_opportunities") |
| `current_offset` | Integer | Current offset position |
| `total_synced` | Integer | Total records synced so far |
| `last_sync_at` | DateTime | Last sync timestamp |
| `is_complete` | Integer | 0 = in progress, 1 = complete |

### **2. `minimal_opportunities` Table**
Stores minimal opportunity data (ID and Number only)

| Column | Type | Purpose |
|--------|------|---------|
| `id` | Integer | Primary key (auto-increment) |
| `opportunity_id` | String | Oracle OptyId (unique) |
| `opportunity_number` | String | Oracle OptyNumber |
| `synced_at` | DateTime | When this record was synced |

---

## 🔄 **How It Works (Following Your Pseudocode)**

### **Your Pseudocode:**
```
batchSize = 5
offset = getOffsetFromDB()  // returns 0 first time

do {
    url = buildUrl(batchSize, offset)
    response = callAPI(url)

    for each item in response.items:
        saveToDB(item.OpportunityId, item.OpportunityNumber)

    offset = offset + batchSize
    updateOffsetInDB(offset)

} while (response.hasMore)
```

### **My Implementation:**
```python
def batch_sync_opportunities(batch_size=5):
    # Get offset from DB (returns 0 first time)
    offset = get_offset_from_db(db, "oracle_opportunities")
    
    while True:
        # Build URL
        url = build_url(batch_size, offset)
        
        # Call API
        response = call_api(url)
        
        # Get items
        items = response.get("items", [])
        if not items:
            break
        
        # For each item
        for item in items:
            opportunity_id = item.get("OptyId")
            opportunity_number = item.get("OptyNumber")
            
            # Save to DB
            save_to_db(db, opportunity_id, opportunity_number)
        
        # Update offset
        offset = offset + batch_size
        update_offset_in_db(db, offset, total_synced)
        
        # Check if more
        if not response.get("hasMore"):
            break
```

---

## 🚀 **How to Use**

### **Option 1: Run Default Sync (Batch Size = 5)**

```bash
cd "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
python batch_sync_with_offset.py
```

**Output:**
```
======================================================================
🚀 Starting Batch Sync with Offset Tracking
======================================================================
📝 Created new sync state for 'oracle_opportunities'
======================================================================
📦 Batch: Offset=0, Size=5
======================================================================
📡 Calling API: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi...
✅ Received 5 items
📝 Processing 5 items...
   ✅ Saved: 123456 - 1902737
   ✅ Saved: 123457 - 1672704
   ✅ Saved: 123458 - 1673697
   ✅ Saved: 123459 - 1902738
   ✅ Saved: 123460 - 1658758
✅ Batch complete: 5/5 saved
💾 Updated offset to 5, total synced: 5
======================================================================
📦 Batch: Offset=5, Size=5
======================================================================
...
🎉 Sync Complete!
   Total Synced: 150
   Final Offset: 150
======================================================================
```

---

### **Option 2: Run with Custom Batch Size**

```bash
# Batch size of 10
python batch_sync_with_offset.py sync 10

# Batch size of 20
python batch_sync_with_offset.py sync 20

# Batch size of 50
python batch_sync_with_offset.py sync 50
```

---

### **Option 3: Check Sync Status**

```bash
python batch_sync_with_offset.py status
```

**Output:**
```
📊 Sync Status for 'oracle_opportunities':
   Offset: 75
   Total Synced: 75
   Last Sync: 2024-01-16 13:08:00
   Complete: False
📊 Total opportunities in minimal_opportunities table: 75
```

---

### **Option 4: Reset Sync (Start from Beginning)**

```bash
python batch_sync_with_offset.py reset
```

**Output:**
```
🔄 Reset sync state for 'oracle_opportunities'
```

---

## 🔍 **Key Features**

### **1. Offset Tracking**
```python
def get_offset_from_db(db, sync_name):
    """Returns 0 first time, then resumes from saved offset"""
    state = db.query(SyncState).filter(
        SyncState.sync_name == sync_name
    ).first()
    
    if not state:
        return 0  # First time
    
    return state.current_offset  # Resume from here
```

### **2. Resumable Sync**
- If sync stops (error, Ctrl+C, etc.), run again to resume
- Automatically picks up from last saved offset
- No duplicate processing

### **3. Minimal Fields**
```python
"fields": "OptyId,OptyNumber"  # Only fetch what you need
```
- Faster API calls
- Less data transfer
- Focused storage

### **4. Batch Processing**
```python
batch_size = 5  # Configurable
```
- Process in small chunks
- Better error recovery
- Progress tracking

---

## 📊 **URL Structure**

### **Built URL:**
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'
&q=RecordSet='ALL'
&fields=OptyId,OptyNumber
&limit=5
&offset=0
&onlyData=true
```

### **Parameters:**
| Parameter | Value | Purpose |
|-----------|-------|---------|
| `finder` | `MyOpportunitiesFinder;RecordSet='ALLOPTIES'` | Which finder to use |
| `q` | `RecordSet='ALL'` | Get ALL opportunities |
| `fields` | `OptyId,OptyNumber` | Only fetch these fields |
| `limit` | `5` | Batch size |
| `offset` | `0` | Start position (increments) |
| `onlyData` | `true` | No metadata |

---

## 🔄 **Sync Flow**

```
Start
  ↓
Get offset from DB (0 first time)
  ↓
┌─────────────────────────┐
│  Build URL with offset  │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  Call Oracle API        │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  Get items from response│
└────────┬────────────────┘
         ↓
    Items empty?
    Yes → Complete ✅
    No  ↓
┌─────────────────────────┐
│  For each item:         │
│  - Get OptyId           │
│  - Get OptyNumber       │
│  - Save to DB           │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│  offset = offset + 5    │
│  Update offset in DB    │
└────────┬────────────────┘
         ↓
    hasMore?
    Yes → Loop back ↑
    No  → Complete ✅
```

---

## 📋 **Database Queries**

### **Check Sync State:**
```sql
SELECT * FROM sync_state WHERE sync_name = 'oracle_opportunities';
```

**Result:**
```
id | sync_name            | current_offset | total_synced | last_sync_at        | is_complete
---+----------------------+----------------+--------------+---------------------+-------------
1  | oracle_opportunities | 75             | 75           | 2024-01-16 13:08:00 | 0
```

### **Check Synced Opportunities:**
```sql
SELECT COUNT(*) FROM minimal_opportunities;
```

**Result:**
```
count
------
75
```

### **View Synced Data:**
```sql
SELECT * FROM minimal_opportunities LIMIT 10;
```

**Result:**
```
id | opportunity_id | opportunity_number | synced_at
---+----------------+--------------------+---------------------
1  | 123456         | 1902737            | 2024-01-16 13:08:00
2  | 123457         | 1672704            | 2024-01-16 13:08:01
3  | 123458         | 1673697            | 2024-01-16 13:08:02
...
```

---

## ⚠️ **Important Notes**

### **1. Separate from Existing Code**
- ✅ Does NOT modify `sync_manager.py`
- ✅ Does NOT modify `main.py`
- ✅ Does NOT touch `opportunities` table
- ✅ Creates its own tables: `sync_state`, `minimal_opportunities`

### **2. Resumable**
- If sync stops, run again
- Automatically resumes from last offset
- No data loss

### **3. Minimal Storage**
- Only stores ID and Number
- For full data, use existing `sync_manager.py`
- This is for testing/demonstration

### **4. Independent**
- Can run alongside existing sync
- Does not interfere with backend
- Standalone module

---

## 🎯 **Use Cases**

### **1. Test Batch Sync Logic**
```bash
python batch_sync_with_offset.py sync 5
```
Test with small batches

### **2. Resume After Failure**
```bash
# Run sync
python batch_sync_with_offset.py sync 10

# If it stops (Ctrl+C or error), run again
python batch_sync_with_offset.py sync 10
# Automatically resumes from last offset
```

### **3. Monitor Progress**
```bash
# In one terminal: run sync
python batch_sync_with_offset.py sync 5

# In another terminal: check status
python batch_sync_with_offset.py status
```

### **4. Start Fresh**
```bash
# Reset and start from beginning
python batch_sync_with_offset.py reset
python batch_sync_with_offset.py sync 5
```

---

## 📊 **Comparison with Existing Sync**

| Feature | Existing (`sync_manager.py`) | New (`batch_sync_with_offset.py`) |
|---------|------------------------------|-----------------------------------|
| **Table** | `opportunities` | `minimal_opportunities` |
| **Fields** | All fields | Only ID and Number |
| **Offset Tracking** | No | Yes (in `sync_state` table) |
| **Resumable** | No | Yes |
| **Batch Size** | 50 (fixed) | Configurable (default 5) |
| **Auto-run** | Yes (on backend startup) | No (manual) |
| **Purpose** | Production sync | Testing/demonstration |

---

## 🔧 **Customization**

### **Change Batch Size:**
```python
# In code
batch_sync_opportunities(batch_size=10)

# Or command line
python batch_sync_with_offset.py sync 10
```

### **Add More Fields:**
```python
# In build_url() function
"fields": "OptyId,OptyNumber,Name,Revenue"
```

### **Change Sync Name:**
```python
batch_sync_opportunities(
    batch_size=5,
    sync_name="my_custom_sync"
)
```

---

## ✅ **Summary**

### **What I Created:**
- ✅ New file: `batch_sync_with_offset.py`
- ✅ Implements your pseudocode exactly
- ✅ Offset tracking in database
- ✅ Resumable sync
- ✅ Batch processing
- ✅ Minimal field selection
- ✅ Does NOT mix with existing code

### **New Tables:**
- ✅ `sync_state` - Tracks offset
- ✅ `minimal_opportunities` - Stores ID and Number

### **How to Run:**
```bash
# Default sync (batch size 5)
python batch_sync_with_offset.py

# Custom batch size
python batch_sync_with_offset.py sync 10

# Check status
python batch_sync_with_offset.py status

# Reset
python batch_sync_with_offset.py reset
```

### **Key Features:**
- ✅ Follows your pseudocode
- ✅ Offset tracking
- ✅ Resumable
- ✅ Independent module
- ✅ Does not affect existing code

---

**Your batch sync with offset tracking is ready to use!** 📦
