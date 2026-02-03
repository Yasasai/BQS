# BQS Complete Workflow Guide

## 🎯 Overview
This guide shows the complete end-to-end workflow for the Bid Qualification System (BQS).

---

## 👥 User Roles

### 1. Practice Head (Kunal)
- **Email**: `kunal.lead@example.com`
- **Responsibilities**: Assign opportunities to SAs, Review assessments, Approve/Reject

### 2. Solution Architect (Demo SA)
- **Email**: `sa.demo@example.com`
- **Responsibilities**: Fill assessments, Submit for review, Create new versions

---

## 📋 Complete Workflow

### Step 1: Practice Head Assigns Opportunity to SA

1. **Login as Practice Head** (Kunal)
   - Switch user in top-right dropdown
   - Select "Kunal (Lead)"

2. **Navigate to Dashboard**
   - Go to Practice Head Dashboard
   - Click on **"Unassigned"** tab

3. **Assign to SA**
   - Find an opportunity in the list
   - Click the **3-dot menu** (⋮) on the right
   - Select **"Assign to SA"**
   - Choose **Primary SA**: `sa.demo@example.com`
   - (Optional) Choose Secondary SA
   - Click **"Assign"**

4. **Verify Assignment**
   - Go to **"Assigned to SA"** tab
   - The opportunity should now appear there
   - Status: `ASSIGNED_TO_SA`

---

### Step 2: Solution Architect Fills Assessment

1. **Login as Solution Architect**
   - Switch user to "Demo SA"

2. **Navigate to SA Dashboard**
   - Go to Solution Architect Dashboard
   - Click on **"Pending"** tab
   - You should see the assigned opportunity

3. **Start Assessment**
   - Click on the opportunity
   - You'll be taken to the **ScoreOpportunity** page
   - Title shows: "Fill Assessment"

4. **Fill the Assessment Form**
   
   **For each of the 8 criteria:**
   - **Strategic Fit/Why Inspira?**
   - **Win Probability**
   - **Competitive Position/Incumbent**
   - **Financial Value**
   - **Resource Availability**
   - **Past Performance/References**
   - **Customer Relationship**
   - **Legal/Insurance/Bond Requirement**

   **For each criterion:**
   - Select a **Score** (0.5 to 5.0 scale)
   - Select **Justifications** (checkboxes for reasons)
   - Add **Notes** (optional text)

5. **Add Summary**
   - Scroll to bottom
   - Select **Confidence Level**: High/Medium/Low
   - Select **Recommendation**: Pursue/Conditional/No-Bid
   - Add **Summary Comment**
   - (Optional) Upload **Evidence Document**

6. **Save or Submit**
   - **Save Draft**: Saves progress, can edit later (Status: `UNDER_ASSESSMENT`)
   - **Submit Assessment**: Sends to Practice Head for review (Status: `SUBMITTED_FOR_REVIEW`)

---

### Step 3: Practice Head Reviews Assessment

1. **Login as Practice Head** (Kunal)

2. **Navigate to Review Tab**
   - Go to Practice Head Dashboard
   - Click on **"Under-Assessment"** tab
   - You should see the submitted assessment

3. **Open Assessment**
   - Click on the opportunity
   - You'll see the **ScoreOpportunity** page in **Read-Only** mode
   - Title shows: "View Assessment"
   - All fields are disabled (greyed out)

4. **Review the Assessment**
   - Check all scores and justifications
   - Review the overall score (calculated automatically)
   - Read the SA's summary and recommendation
   - Check the assessment history (if multiple versions exist)

5. **Make Decision**
   
   **Option A: Approve**
   - Click **"Approve Assessment"** button (green)
   - Confirm the action
   - Status changes to: `APPROVED`
   - Opportunity moves to **"Approved"** tab

   **Option B: Reject**
   - Click **"Reject Assessment"** button (red)
   - Enter rejection reason in the popup
   - Confirm the action
   - Status changes to: `REJECTED`
   - Opportunity moves to **"Rejected"** tab

---

### Step 4: Solution Architect Creates New Version (If Rejected)

1. **Login as Solution Architect**

2. **Navigate to Submitted Tab**
   - Go to SA Dashboard
   - Click on **"Submitted"** tab
   - Find the rejected opportunity

3. **Create New Version**
   - Click on the opportunity
   - Click **"Create New Version"** button (blue, with refresh icon)
   - Confirm the action
   - A new version (v2) is created with all previous data copied
   - Status changes back to: `UNDER_ASSESSMENT`

4. **Edit and Resubmit**
   - Make necessary changes based on rejection feedback
   - Click **"Submit Assessment"** again
   - Goes back to Practice Head for review

---

## 🗂️ Dashboard Tab Structure

### Practice Head Dashboard
| Tab | Shows Opportunities With Status |
|-----|--------------------------------|
| **Unassigned** | No SA assigned yet |
| **Assigned to SA** | `ASSIGNED_TO_SA` |
| **Under-Assessment** | `UNDER_ASSESSMENT`, `SUBMITTED_FOR_REVIEW` |
| **Approved** | `APPROVED`, `ACCEPTED` |
| **Rejected** | `REJECTED` |

### Solution Architect Dashboard
| Tab | Shows Opportunities With Status |
|-----|--------------------------------|
| **Pending** | `ASSIGNED_TO_SA` (not started) |
| **In-Progress** | `UNDER_ASSESSMENT` (draft saved) |
| **Submitted** | `SUBMITTED_FOR_REVIEW`, `APPROVED`, `REJECTED` |

---

## 🔄 Status Flow Diagram

```
NEW (Unassigned)
    ↓ [PH assigns to SA]
ASSIGNED_TO_SA
    ↓ [SA starts filling]
UNDER_ASSESSMENT (Draft)
    ↓ [SA submits]
SUBMITTED_FOR_REVIEW
    ↓
    ├─→ [PH approves] → APPROVED ✅
    └─→ [PH rejects] → REJECTED ❌
            ↓ [SA creates new version]
        UNDER_ASSESSMENT (v2)
```

---

## 🎨 UI Features

### Practice Head Dashboard
- **Assign Modal**: Select SA from dropdown
- **Action Menu**: Quick actions on each opportunity (⋮)
- **Approve/Reject Buttons**: In both dashboard and detail view
- **Version Column**: Shows v1, v2, etc.

### Solution Architect Dashboard
- **Start Assessment**: Click opportunity to begin
- **Save Draft**: Save progress without submitting
- **Submit**: Send to PH for review
- **Create New Version**: Available after rejection
- **Version Badge**: Shows current version (v1, v2)

### ScoreOpportunity Page
- **Role-Based View**:
  - **SA**: Can edit when status is DRAFT
  - **PH**: Always read-only
- **Smart Buttons**:
  - SA sees: Save Draft, Submit
  - PH sees: Approve, Reject (only when SUBMITTED)
- **Version History**: Shows all previous versions at bottom

---

## ✅ Verification Checklist

### Backend Running
- [ ] Backend server started: `python -m uvicorn app.main:app --reload`
- [ ] Console shows: "✅ Synced workflow_status for X opportunities"
- [ ] API accessible at: `http://127.0.0.1:8000`

### Frontend Running
- [ ] Frontend server started: `npm run dev`
- [ ] Accessible at: `http://localhost:5173`

### Database
- [ ] PostgreSQL running
- [ ] Database `bqs` exists
- [ ] `workflow_status` column populated

### Test Workflow
- [ ] Can switch between users
- [ ] PH can assign opportunity to SA
- [ ] SA can fill and submit assessment
- [ ] PH can see submitted assessment in "Under-Assessment" tab
- [ ] PH can approve/reject
- [ ] Approved items appear in "Approved" tab
- [ ] Rejected items appear in "Rejected" tab
- [ ] SA can create new version after rejection

---

## 🐛 Troubleshooting

### "No opportunities showing in dashboard"
- Check backend console for sync message
- Verify `workflow_status` is populated: `SELECT workflow_status, COUNT(*) FROM opportunity GROUP BY workflow_status;`
- Restart backend server

### "Assignment not working"
- Check browser console for errors
- Verify SA email exists in database
- Check backend logs for assignment errors

### "Approve/Reject buttons not visible"
- Ensure you're logged in as Practice Head
- Verify opportunity status is `SUBMITTED_FOR_REVIEW`
- Check that you're viewing the assessment detail page

### "SA can't edit assessment"
- Check status - must be `DRAFT` or `UNDER_ASSESSMENT`
- Verify user is logged in as SA
- Check deadline hasn't passed

---

## 📞 Quick Reference

### API Endpoints
- Assign: `POST /api/inbox/assign`
- Submit: `POST /api/scoring/{opp_id}/submit`
- Approve: `POST /api/scoring/{opp_id}/review/approve`
- Reject: `POST /api/scoring/{opp_id}/review/reject`
- New Version: `POST /api/scoring/{opp_id}/new-version`

### Frontend Routes
- PH Dashboard: `/practice-head/review`
- SA Dashboard: `/sa/assigned`
- Assessment: `/score/{opp_id}`

---

**Ready to test the complete workflow!** 🚀
