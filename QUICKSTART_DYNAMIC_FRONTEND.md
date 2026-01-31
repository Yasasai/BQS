# 🚀 Quick Start Guide - Dynamic Frontend

## ✅ What Was Implemented

Your dynamic frontend is now **fully functional** with:

1. ✅ **Backend-driven status management** - All status changes come from backend
2. ✅ **Instant UI updates** - Assignments update immediately without page refresh
3. ✅ **Dynamic segregation** - Opportunities automatically move between tabs
4. ✅ **Email-based assignment** - Practice Head assigns by SA email
5. ✅ **Real-time filtering** - Practice Head sees unassigned, SA sees only theirs

---

## 🔧 Files Modified

### Backend
- ✅ `backend/routers/inbox.py` - Fixed assignment API to accept email and return updated data

### Frontend
- ✅ `frontend/src/pages/PracticeHeadDashboard.tsx` - Optimistic UI updates + instant refresh

---

## 🎯 How to Test

### Step 1: Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Verify**: Open http://127.0.0.1:8000/docs - should show API documentation

---

### Step 2: Start Frontend

```bash
cd frontend
npm run dev
```

**Verify**: Open http://localhost:5176 (or whatever URL is shown in your terminal) - should show login page

> **Note**: If port 5176 is busy, Vite might automatically pick 5177 or 5178. **Check the terminal output** to be sure!

---

### Step 3: Test Assignment Flow

1. **Login as Practice Head**
   - Navigate to: http://localhost:5176/practice-head/action-required (adjust port if needed)

2. **View Unassigned Opportunities**
   - You should see "1. Assign to Solution Architect" card
   - Shows opportunities where `assigned_sa === null`

3. **Assign an Opportunity**
   - Click "Assign" button on any unassigned opportunity
   - Modal opens with list of SAs
   - Select an SA from dropdown
   - Click "Confirm Allocation"

4. **Verify Instant Update** ✨
   - Opportunity **instantly disappears** from "Unassigned" card
   - Status badge changes to "ASSIGNED TO SA"
   - **No page refresh needed!**

5. **Check Assigned Tab**
   - Click "Assigned to SA" in sidebar
   - Opportunity now appears in this list
   - Status shows "ASSIGNED TO SA"

6. **Verify SA Dashboard**
   - Navigate to: http://localhost:5176/sa/assigned
   - Login as the SA you assigned to
   - Opportunity appears in "Pending" tab
   - Can click "Run Assessment" to start scoring

---

### Step 4: Run Automated Test (Optional)

```bash
# Make sure backend is running first!
python test_assignment_flow.py
```

This will:
- ✅ Fetch all opportunities
- ✅ Find an unassigned opportunity
- ✅ Get list of SAs
- ✅ Assign opportunity to first SA
- ✅ Verify assignment was successful
- ✅ Verify status changed to ASSIGNED_TO_SA

---

## 🔍 What to Look For

### ✅ Practice Head Dashboard

**Unassigned Tab**:
- Shows opportunities where `assigned_sa === null` or `assigned_sa === 'Unassigned'`
- Status is NOT in finished states (APPROVED, REJECTED, etc.)

**Assigned Tab**:
- Shows opportunities where `assigned_sa !== null`
- Status is `ASSIGNED_TO_SA`

**Under Assessment Tab**:
- Shows opportunities with status `UNDER_ASSESSMENT` or `SUBMITTED_FOR_REVIEW`

**Action Required**:
- Card 1: Unassigned opportunities needing assignment
- Card 2: Submitted assessments needing review

### ✅ Solution Architect Dashboard

**Filtering**:
- Only shows opportunities where `assigned_sa === currentUser.display_name`

**Pending Tab**:
- Status = `ASSIGNED_TO_SA`
- Shows "Run Assessment" button

**In Progress Tab**:
- Status = `UNDER_ASSESSMENT`
- Shows "Restore Session" button

**Submitted Tab**:
- Status = `SUBMITTED_FOR_REVIEW`, `APPROVED`, `REJECTED`, etc.
- Shows "Review Submission" button

---

## 🎯 Key Behaviors

### 1. Assignment Flow
```
User clicks "Assign" 
  → Modal opens
  → User selects SA
  → Frontend calls API
  → Optimistic UI update (instant)
  → Backend processes
  → Frontend refetches (500ms later)
  → Opportunity moves to correct tab
```

### 2. Status Transitions (Backend-Driven)
```
NEW 
  → ASSIGNED_TO_SA (when assigned)
  → UNDER_ASSESSMENT (when SA starts)
  → SUBMITTED_FOR_REVIEW (when SA submits)
  → APPROVED/REJECTED (when PH reviews)
```

### 3. Dynamic Segregation
- Opportunities automatically move between tabs based on:
  - `assigned_sa` field (null vs. not null)
  - `workflow_status` field (backend-controlled)
- **No hardcoded status values in frontend**
- **All status comes from backend API**

---

## 🐛 Troubleshooting

### Backend not responding?
```bash
# Check if backend is running
curl http://127.0.0.1:8000/api/opportunities/

# If not, start it:
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend not showing opportunities?
1. Open browser console (F12)
2. Check for errors
3. Verify API call to `http://127.0.0.1:8000/api/opportunities/`
4. Check response data

### Assignment not working?
1. Open browser console
2. Check for error messages
3. Verify SA email exists in database
4. Check backend logs for errors

### Opportunities not moving between tabs?
1. Verify `assigned_sa` field is updated
2. Check `workflow_status` field
3. Ensure frontend is reading from backend data
4. Try manual refresh to verify backend state

---

## 📊 API Endpoints

### Get All Opportunities
```
GET http://127.0.0.1:8000/api/opportunities/
```

**Response**:
```json
[
  {
    "id": "123",
    "name": "Opportunity Name",
    "assigned_sa": null,  // null = unassigned
    "workflow_status": "NEW"
  }
]
```

### Assign Opportunity
```
POST http://127.0.0.1:8000/api/inbox/assign
Content-Type: application/json

{
  "opp_id": "123",
  "sa_email": "john.doe@example.com",
  "assigned_by_user_id": "PRACTICE_HEAD"
}
```

**Response**:
```json
{
  "status": "success",
  "opportunity": {
    "id": "123",
    "assigned_sa": "John Doe",
    "workflow_status": "ASSIGNED_TO_SA"
  }
}
```

---

## 🎉 Success!

Your dynamic frontend is now **fully operational**! 

**Key Features**:
- ✅ Backend is source of truth
- ✅ Instant UI updates (no page refresh)
- ✅ Dynamic tab segregation
- ✅ Status-driven workflow
- ✅ Real-time filtering

**Next Steps**:
1. Start backend and frontend
2. Test assignment flow
3. Verify opportunities move between tabs
4. Check SA dashboard shows correct opportunities
5. Enjoy your dynamic, reactive UI! 🚀

---

## 📚 Documentation

- **Implementation Plan**: `DYNAMIC_FRONTEND_IMPLEMENTATION.md`
- **Complete Summary**: `IMPLEMENTATION_COMPLETE.md`
- **Test Script**: `test_assignment_flow.py`
- **This Guide**: `QUICKSTART_DYNAMIC_FRONTEND.md`
