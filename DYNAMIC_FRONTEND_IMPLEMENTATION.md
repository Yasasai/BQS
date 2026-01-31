# 🔥 Dynamic Frontend Implementation Plan

## ✅ Core Understanding

### Backend is Source of Truth
- Frontend consumes: `GET http://127.0.0.1:8000/api/opportunities/`
- Frontend **never hardcodes status** — reacts to backend data
- All status transitions happen in backend

### Meaning of `assigned_sa = null`
- `assigned_sa = null` ⟶ **Unassigned opportunity**
- Visible to **Practice Head only**
- Shown under **Unassigned / OPEN**

### Frontend Segregation Logic

**Practice Head Dashboard**
- **Unassigned** → `assigned_sa === null`
- **Assigned** → `assigned_sa !== null`
- **Pending Review** → `workflow_status === 'SUBMITTED_FOR_REVIEW'`

**Solution Architect Dashboard**
- **My Opportunities** → `assigned_sa === logged_in_user`
- **In Assessment / Submitted** → based on `workflow_status`

### Dynamic Assignment Behavior
1. Practice Head assigns SA
2. Frontend calls backend assign API
3. Backend updates assignment + status
4. **Frontend instantly updates UI**
   - Opportunity removed from *Unassigned*
   - Appears under *Assigned*
   - Status badge changes automatically
5. **No page refresh needed**

### Status Flow (Backend-Driven)
```
NEW → ASSIGNED_TO_SA → UNDER_ASSESSMENT → SUBMITTED_FOR_REVIEW → APPROVED / REJECTED
```

---

## 🔧 Implementation Steps

### 1. Fix Backend Assignment API

**File**: `backend/routers/inbox.py`

**Current Issue**:
- Endpoint expects: `assigned_to_user_id` (user_id)
- Frontend sends: `sa_email` (email)

**Solution**:
- Update endpoint to accept email
- Look up user_id from email
- Return updated opportunity data

### 2. Update Frontend Assignment Flow

**File**: `frontend/src/pages/PracticeHeadDashboard.tsx`

**Changes**:
1. Fix assignment API call to match backend expectations
2. Implement instant UI update after assignment
3. Remove opportunity from unassigned list
4. Add to assigned list
5. Update status badge

### 3. Implement Real-Time Data Refresh

**Strategy**:
- After assignment, refetch opportunities
- Use optimistic UI updates
- Show loading states during transitions

### 4. Ensure Status Consistency

**Frontend Rules**:
- Never set status manually
- Always read from `workflow_status` field
- Let backend handle all status transitions

---

## 📋 API Contract

### Assignment Endpoint

**Request**:
```json
POST /api/inbox/assign
{
  "opp_id": "123",
  "sa_email": "john.doe@example.com",
  "assigned_by_user_id": "ph_user_id"
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

### Opportunities Endpoint

**Response**:
```json
[
  {
    "id": "123",
    "name": "Opportunity Name",
    "assigned_sa": null,  // null = unassigned
    "workflow_status": "NEW"
  },
  {
    "id": "456",
    "name": "Another Opportunity",
    "assigned_sa": "John Doe",
    "workflow_status": "ASSIGNED_TO_SA"
  }
]
```

---

## 🎯 Success Criteria

✅ Assignment instantly updates UI without page refresh
✅ Opportunities move between tabs dynamically
✅ Status badges reflect backend state
✅ No hardcoded status values in frontend
✅ Practice Head sees unassigned opportunities
✅ SA sees only their assigned opportunities
✅ All status transitions come from backend

---

## 🚀 Execution Order

1. ✅ Fix backend assignment API
2. ✅ Update frontend assignment handler
3. ✅ Implement instant UI refresh
4. ✅ Test assignment flow end-to-end
5. ✅ Verify status consistency
