# 3-ROLE WORKFLOW SYSTEM - IMPLEMENTATION COMPLETE

## ✅ EXECUTED: Strict Segregation of Duties

---

## STATUS MACHINE

### State Transition Flow:
```
NEW_FROM_CRM 
    ↓ [Management: Assign to Practice]
ASSIGNED_TO_PRACTICE
    ↓ [Practice Head: Assign to SA]
ASSIGNED_TO_SA
    ↓ [SA: Start Assessment]
UNDER_ASSESSMENT
    ↓ [SA: Submit for Review]
SUBMITTED_FOR_REVIEW
    ↓ [Practice Head: Approve] OR [Reject → back to ASSIGNED_TO_SA]
PENDING_FINAL_DECISION
    ↓ [Management: GO/NO-GO]
APPROVED_FINAL or REJECTED_FINAL
```

---

## ROLE 1: MANAGEMENT DASHBOARD

### Access: `/management-dashboard`

### Inbound Stream:
- All opportunities with `workflow_status = 'NEW_FROM_CRM'`
- All opportunities with `workflow_status = 'PENDING_FINAL_DECISION'`

### Tabs:
1. **New from CRM** - Raw opportunities needing practice assignment
2. **Pending Final Decision** - Scored opportunities awaiting GO/NO-GO
3. **Completed** - Final decisions made
4. **All** - Complete view

### Table Columns:
- Opp ID
- Name/Customer
- Practice (assigned)
- Deal Size
- **Status** (badge)
- **Assigned To** (Practice Head or SA)
- Score (win probability)
- **Actions**

### Action Buttons (Context-Specific):
- **View Details** (always visible)
- **✓ Assign to Practice** (only if status = NEW_FROM_CRM)
  - Prompts for: Practice name, Practice Head name
  - API: `POST /api/opportunities/{id}/assign-practice`
- **✓ Approve (GO)** (only if status = PENDING_FINAL_DECISION)
  - API: `POST /api/opportunities/{id}/final-decision` with `decision: "GO"`
- **✗ Reject (NO-GO)** (only if status = PENDING_FINAL_DECISION)
  - API: `POST /api/opportunities/{id}/final-decision` with `decision: "NO_GO"`

### Handshake Logic:
- **Assign to Practice**: Changes status to `ASSIGNED_TO_PRACTICE`, sets `assigned_practice` and `assigned_practice_head`, unlocks record
- **Final Decision**: Changes status to `APPROVED_FINAL` or `REJECTED_FINAL`, records decision and timestamp

---

## ROLE 2: PRACTICE HEAD DASHBOARD

### Access: `/practice-head-dashboard`

### Inbound Stream (Filtered):
- Only opportunities where:
  - `assigned_practice = currentPractice` OR
  - `assigned_practice_head = currentPracticeHead`

### Tabs:
1. **Unassigned** - Needs SA assignment (status = ASSIGNED_TO_PRACTICE, no SA)
2. **Under Assessment** - SA working on it (status = ASSIGNED_TO_SA or UNDER_ASSESSMENT)
3. **Pending Review** - Awaiting your approval (status = SUBMITTED_FOR_REVIEW)
4. **All** - Complete view

### Table Columns:
- Opp ID
- Name/Customer
- Deal Size
- **Status** (badge)
- **Assigned SA** (shows "Unassigned" if empty)
- Score
- **Actions**

### Action Buttons (Context-Specific):
- **View Details** (always visible)
- **👤 Assign to SA** (only if status = ASSIGNED_TO_PRACTICE and no SA)
  - Prompts for: Primary SA name, Secondary SA (optional)
  - API: `POST /api/opportunities/{id}/assign-sa`
- **View Assessment** (only if status = SUBMITTED_FOR_REVIEW)
- **✓ Approve** (only if status = SUBMITTED_FOR_REVIEW)
  - Sends to Management for final decision
  - API: `POST /api/opportunities/{id}/practice-review` with `decision: "APPROVED"`
- **✗ Reject (Rework)** (only if status = SUBMITTED_FOR_REVIEW)
  - Sends back to SA
  - API: `POST /api/opportunities/{id}/practice-review` with `decision: "REJECTED"`

### Handshake Logic:
- **Assign to SA**: Changes status to `ASSIGNED_TO_SA`, sets `assigned_sa`, unlocks record
- **Approve**: Changes status to `PENDING_FINAL_DECISION`, forwards to Management
- **Reject**: Changes status back to `ASSIGNED_TO_SA`, unlocks for SA to rework

---

## ROLE 3: SOLUTION ARCHITECT DASHBOARD

### Access: `/solution-architect-dashboard`

### Inbound Stream (Filtered):
- Only opportunities where:
  - `assigned_sa = currentSA` OR
  - `assigned_sa_secondary = currentSA`

### Tabs:
1. **My Assignments** - New work (status = ASSIGNED_TO_SA, not locked)
2. **In Progress** - Currently working (status = UNDER_ASSESSMENT)
3. **Submitted** - Under review or approved (status = SUBMITTED_FOR_REVIEW or APPROVED_BY_PRACTICE)
4. **All** - Complete view

### Table Columns:
- Opp ID
- Name/Customer
- Practice
- Deal Size
- **Status** (badge, shows 🔒 if locked by someone else)
- **Assigned By** (Practice Head name)
- **Actions**

### Action Buttons (Context-Specific):
- **View Details** (always visible)
- **✏ Start Assessment** (only if status = ASSIGNED_TO_SA)
  - Locks the record
  - API: `POST /api/opportunities/{id}/start-assessment`
  - Navigates to assessment form
- **✏ Continue Assessment** (only if status = UNDER_ASSESSMENT)
  - Navigates to assessment form
- **📤 Submit for Review** (only if status = UNDER_ASSESSMENT)
  - Unlocks and submits
  - API: `POST /api/opportunities/{id}/submit-assessment`
- **View Submitted Assessment** (only if status = SUBMITTED_FOR_REVIEW)
  - Read-only view

### Handshake Logic:
- **Start Assessment**: Changes status to `UNDER_ASSESSMENT`, sets `locked_by = currentSA`, records lock timestamp
- **Submit for Review**: Changes status to `SUBMITTED_FOR_REVIEW`, clears `locked_by`, records submission timestamp
- **Lock Mechanism**: If `locked_by` is set and not equal to current user, all edit actions are disabled, shows "🔒 Locked by {name}"

---

## LOCK MECHANISM (Prevents Concurrent Edits)

### Fields:
- `locked_by` (VARCHAR) - Name/email of person currently working
- `locked_at` (TIMESTAMP) - When lock was acquired

### Rules:
1. **SA starts assessment** → Record is locked to that SA
2. **SA submits for review** → Lock is released
3. **Practice Head rejects** → Lock is released (SA can pick up again)
4. **Another SA tries to access** → Shows "🔒 Locked by {name}", disables edit buttons

### Visual Indicators:
- Locked rows show lock icon in status badge
- Action buttons are disabled
- Row opacity reduced to 60%

---

## API ENDPOINTS SUMMARY

| Endpoint | Role | Transition | Lock Behavior |
|----------|------|------------|---------------|
| `POST /api/opportunities/{id}/assign-practice` | Management | NEW_FROM_CRM → ASSIGNED_TO_PRACTICE | Unlocks |
| `POST /api/opportunities/{id}/assign-sa` | Practice Head | ASSIGNED_TO_PRACTICE → ASSIGNED_TO_SA | Unlocks |
| `POST /api/opportunities/{id}/start-assessment` | SA | ASSIGNED_TO_SA → UNDER_ASSESSMENT | **Locks to SA** |
| `POST /api/opportunities/{id}/submit-assessment` | SA | UNDER_ASSESSMENT → SUBMITTED_FOR_REVIEW | **Unlocks** |
| `POST /api/opportunities/{id}/practice-review` | Practice Head | SUBMITTED_FOR_REVIEW → PENDING_FINAL_DECISION or ASSIGNED_TO_SA | Unlocks if rejected |
| `POST /api/opportunities/{id}/final-decision` | Management | PENDING_FINAL_DECISION → APPROVED_FINAL or REJECTED_FINAL | N/A |

---

## DATABASE SCHEMA CHANGES

### New Columns in `opportunities` table:

```sql
-- Status machine
workflow_status VARCHAR DEFAULT 'NEW_FROM_CRM'

-- Ownership chain
assigned_practice VARCHAR
assigned_practice_head VARCHAR
assigned_sa VARCHAR
assigned_sa_secondary VARCHAR

-- Timestamps (SLA tracking)
assigned_to_practice_at TIMESTAMP
assigned_to_sa_at TIMESTAMP
submitted_for_review_at TIMESTAMP
approved_by_practice_at TIMESTAMP
final_decision_at TIMESTAMP

-- Decision tracking
practice_head_decision VARCHAR  -- APPROVED, REJECTED, PENDING
practice_head_comments TEXT
management_decision VARCHAR     -- GO, NO_GO, PENDING
management_comments TEXT

-- Lock mechanism
locked_by VARCHAR
locked_at TIMESTAMP
```

---

## UI/UX HIGHLIGHTS

### Color-Coded Status Badges:
- **NEW_FROM_CRM**: Blue - "New from CRM"
- **ASSIGNED_TO_PRACTICE**: Purple - "With Practice" / "Needs SA Assignment"
- **ASSIGNED_TO_SA**: Blue - "With SA" / "New Assignment"
- **UNDER_ASSESSMENT**: Indigo - "In Progress"
- **SUBMITTED_FOR_REVIEW**: Orange - "Awaiting Review"
- **PENDING_FINAL_DECISION**: Orange - "Awaiting Decision"
- **APPROVED_FINAL**: Green - "Approved (GO)"
- **REJECTED_FINAL**: Red - "Rejected (NO-GO)"

### Alert Badges:
- **Unassigned tab** (Practice Head): Purple badge if count > 0
- **Pending Review tab** (Practice Head): Orange badge if count > 0
- **My Assignments tab** (SA): Blue badge if count > 0
- **Pending Final Decision tab** (Management): Orange badge if count > 0

### Action Button Styling:
- **Primary actions** (Assign, Approve, Start): Colored text matching role theme
- **Destructive actions** (Reject, NO-GO): Red text
- **Disabled actions**: Grayed out with cursor-not-allowed

---

## FILES CREATED

### Frontend:
1. `/frontend/src/pages/ManagementDashboard.tsx` - Management view
2. `/frontend/src/pages/PracticeHeadDashboard.tsx` - Practice Head view
3. `/frontend/src/pages/SolutionArchitectDashboard.tsx` - SA view

### Backend:
- Updated `/backend/database.py` - New status machine schema
- Updated `/backend/main.py` - 6 new workflow API endpoints

### Types:
- Updated `/frontend/src/types.ts` - New workflow fields

---

## NEXT STEPS (Not Yet Implemented)

1. **Authentication & Role Detection**
   - Replace hardcoded `currentSA`, `currentPracticeHead` with auth context
   - Implement role-based routing

2. **Routing Configuration**
   - Add routes in `App.tsx` for the 3 dashboards
   - Redirect based on user role

3. **Database Migration**
   - Run migration to add new columns
   - Backfill existing opportunities with `workflow_status = 'NEW_FROM_CRM'`

4. **Enhanced Lock Mechanism**
   - Auto-unlock after 2 hours of inactivity
   - "Force unlock" button for Practice Heads

5. **Notification System**
   - Email alerts when opportunities are assigned
   - Reminders for pending reviews

6. **Audit Trail**
   - Log all status transitions
   - Show history timeline on opportunity detail page

---

## TESTING CHECKLIST

- [ ] Management can assign to Practice
- [ ] Practice Head sees only their practice's opportunities
- [ ] Practice Head can assign to SA
- [ ] SA sees only their assignments
- [ ] SA can start assessment (locks record)
- [ ] SA can submit for review (unlocks record)
- [ ] Practice Head can approve (forwards to Management)
- [ ] Practice Head can reject (sends back to SA)
- [ ] Management can make final GO/NO-GO decision
- [ ] Lock mechanism prevents concurrent edits
- [ ] Status badges display correctly
- [ ] Tab counts are accurate
- [ ] Filters work correctly

---

## SUMMARY

✅ **3 Distinct Dashboards** created with role-specific views
✅ **Status Machine** implemented with 9 states
✅ **6 API Endpoints** for workflow transitions
✅ **Lock Mechanism** prevents concurrent edits
✅ **Strict Segregation** - each role sees only their work
✅ **Handshake Logic** - clear state transitions with validation

**The system is ready for integration and testing!**
