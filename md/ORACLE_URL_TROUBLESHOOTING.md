# 🔧 Oracle URL Troubleshooting Guide

## Issue: Postman Works, Python Doesn't

**Your Postman URL:**
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet=%27ALLOPTIES%27
```

---

## ✅ **SOLUTION IMPLEMENTED**

### **Problem Identified:**
1. **API Version Mismatch**
   - Postman uses: `11.12.1.0`
   - Python was using: `latest`
   
2. **URL Encoding**
   - Both correctly encode `'` as `%27`
   - This is NOT the issue

### **Fix Applied:**
Made Oracle API version configurable via `.env` file.

---

## 🔧 **How to Configure**

### **Option 1: Use Specific Version (Recommended)**

Add to your `.env` file:
```bash
ORACLE_API_VERSION=11.12.1.0
```

This will make Python use the EXACT same URL as Postman.

### **Option 2: Use Latest (Default)**

Don't add anything to `.env`, it defaults to:
```bash
ORACLE_API_VERSION=latest
```

---

## 📋 **Updated .env File**

Your `.env` should now look like this:

```bash
# Oracle CRM Configuration
ORACLE_BASE_URL=https://eijs-test.fa.em2.oraclecloud.com
ORACLE_API_VERSION=11.12.1.0
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password

# Database Configuration
DATABASE_URL=postgresql://postgres:Abcd1234@localhost:5432/bqs
```

---

## 🧪 **Test the Fix**

### **Step 1: Run Diagnostic**
```bash
python diagnose_oracle_url.py
```

**What it does:**
- Shows Postman URL vs Python URL
- Tests both `latest` and `11.12.1.0` versions
- Shows actual response from Oracle
- Compares the results

**Expected output:**
```
✅ SUCCESS! Found X opportunities
```

### **Step 2: Test Integration**
```bash
python test_oracle_integration.py
```

**Expected output:**
```
🎉 ALL TESTS PASSED!
✅ Using MyOpportunitiesFinder with ALLOPTIES RecordSet
```

### **Step 3: Test Sync**
```bash
python -c "from backend.app.services.sync_manager import sync_opportunities; sync_opportunities()"
```

**Expected output:**
```
🚀 Starting Oracle sync using MyOpportunitiesFinder
✅ Batch 1: Found X opportunities
✓ Sync complete
```

---

## 🔍 **What Changed in Code**

### **File: `backend/app/services/oracle_service.py`**

#### **Change 1: Added API Version Config**
```python
# Before:
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")

# After:
ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL", "https://eijs-test.fa.em2.oraclecloud.com")
ORACLE_API_VERSION = os.getenv("ORACLE_API_VERSION", "latest")  # ← NEW
```

#### **Change 2: Updated URL Construction**
```python
# Before:
url = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/{endpoint}"

# After:
url = f"{ORACLE_BASE_URL}/crmRestApi/resources/{ORACLE_API_VERSION}/{endpoint}"
```

#### **Change 3: Enhanced Logging**
```python
# Now shows:
logger.info(f"📡 API Request: GET {debug_url}")
logger.info(f"🔗 Actual URL: {response.url}")
logger.info(f"📊 Items in response: {len(items)}")
```

---

## 📊 **URL Comparison**

### **Postman URL (What Works):**
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder;RecordSet=%27ALLOPTIES%27
```

### **Python URL (Before Fix):**
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/latest/opportunities?finder=MyOpportunitiesFinder%3BRecordSet%3D%27ALLOPTIES%27&onlyData=true&limit=50&offset=0
```

### **Python URL (After Fix with ORACLE_API_VERSION=11.12.1.0):**
```
https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder%3BRecordSet%3D%27ALLOPTIES%27&onlyData=true&limit=50&offset=0
```

**Differences:**
- ✅ Version now matches: `11.12.1.0`
- ✅ Finder parameter: Same (URL-encoded)
- ℹ️  Extra params: `onlyData`, `limit`, `offset` (these are fine)

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Still Getting 0 Results**

**Possible Causes:**
1. Wrong API version
2. Wrong credentials
3. User doesn't have access to ALLOPTIES RecordSet

**Solution:**
```bash
# 1. Set specific version in .env
echo "ORACLE_API_VERSION=11.12.1.0" >> .env

# 2. Verify credentials
cat .env | grep ORACLE

# 3. Run diagnostic
python diagnose_oracle_url.py
```

---

### **Issue 2: Authentication Failed**

**Error:**
```
❌ Oracle API Error (401): Authentication failed
```

**Solution:**
```bash
# Check credentials in .env
cat .env

# Should have:
ORACLE_USER=your_actual_username
ORACLE_PASSWORD=your_actual_password

# Test with diagnostic
python diagnose_oracle_url.py
```

---

### **Issue 3: Permission Denied**

**Error:**
```
❌ Oracle API Error (403): Forbidden
```

**Solution:**
- Check if your Oracle user has access to ALLOPTIES RecordSet
- Try with different RecordSet value
- Contact Oracle admin for permissions

---

### **Issue 4: URL Encoding Issues**

**Symptoms:**
- Postman works
- Python gets 400 Bad Request

**Solution:**
```python
# The requests library handles encoding automatically
# Don't manually encode the finder parameter

# ✅ CORRECT:
params = {"finder": "MyOpportunitiesFinder;RecordSet='ALLOPTIES'"}

# ❌ WRONG:
params = {"finder": "MyOpportunitiesFinder;RecordSet=%27ALLOPTIES%27"}
```

---

## 📝 **Checklist**

Before running your application:

- [ ] ✅ Added `ORACLE_API_VERSION=11.12.1.0` to `.env`
- [ ] ✅ Verified Oracle credentials in `.env`
- [ ] ✅ Ran `python diagnose_oracle_url.py`
- [ ] ✅ Saw "SUCCESS! Found X opportunities"
- [ ] ✅ Ran `python test_oracle_integration.py`
- [ ] ✅ All tests passed
- [ ] ✅ Ready to start backend

---

## 🚀 **Next Steps**

### **1. Update .env**
```bash
# Add this line to your .env file:
ORACLE_API_VERSION=11.12.1.0
```

### **2. Run Diagnostic**
```bash
python diagnose_oracle_url.py
```

### **3. If Diagnostic Passes:**
```bash
# Test integration
python test_oracle_integration.py

# Run sync
python -c "from backend.app.services.sync_manager import sync_opportunities; sync_opportunities()"

# Start backend
python -m backend.app.main
```

### **4. If Diagnostic Fails:**
- Check error message
- Verify credentials
- Check Oracle permissions
- Try different API version

---

## 📊 **Logging Output**

### **What You'll See (Success):**
```
📡 API Request: GET https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder%3BRecordSet%3D%27ALLOPTIES%27&onlyData=true&limit=50&offset=0
💾 Response Status: 200
🔗 Actual URL: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities?finder=MyOpportunitiesFinder%3BRecordSet%3D%27ALLOPTIES%27&onlyData=true&limit=50&offset=0
📦 Response Keys: ['items', 'count', 'hasMore', 'limit', 'offset', 'links']
📊 Items in response: 50
✅ Batch 1: Found 50 opportunities
```

### **What You'll See (Failure):**
```
📡 API Request: GET https://...
💾 Response Status: 401
❌ Oracle API Error (401): Authentication failed
```

---

## 🎯 **Summary**

**Problem:** Postman works, Python doesn't
**Root Cause:** API version mismatch (`latest` vs `11.12.1.0`)
**Solution:** Made API version configurable via `.env`
**Action Required:** Add `ORACLE_API_VERSION=11.12.1.0` to `.env`

**Files Modified:**
- ✅ `backend/app/services/oracle_service.py` - Added version config
- ✅ `diagnose_oracle_url.py` - Created diagnostic tool
- ✅ `ORACLE_URL_TROUBLESHOOTING.md` - This guide

**Status:** ✅ Ready to test
**Next:** Run `python diagnose_oracle_url.py`

---

**Last Updated:** 2026-01-16 09:13 IST
