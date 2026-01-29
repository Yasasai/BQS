# 📊 BQS Dashboard Requirements - Tabular Summary

## Overview
This document defines the requirements for all four dashboards in the BQS system, showing what each role sees and what actions they can take.

---

## 📋 **Dashboard Comparison Table**

| Feature | Main Dashboard | Management Dashboard | Practice Head Dashboard | Solution Architect Dashboard |
|---------|---------------|---------------------|------------------------|----------------------------|
| **Route** | `/` | `/management/dashboard` | `/practice-head/dashboard` | `/sa/dashboard` |
| **Who Sees It** | All users (default) | Management role | Practice Head role | Solution Architect role |
| **Data Source** | All opportunities | All opportunities | Practice-specific opps | SA-assigned opps only |
| **Primary Purpose** | Overview of all opps | Portfolio management | Practice management | Personal workload |

---

## 📊 **1. MAIN DASHBOARD** (`/`)

### **Purpose:**
Universal dashboard showing all opportunities - serves as the default landing page for all users.

### **Metrics Cards:**
| Metric | Calculation | Color | Description |
|--------|------------|-------|-------------|
| Total Opportunities | Count of all opps | Blue (#1976D2) | All opportunities in system |
| Pipeline Value | Sum of all deal_value | Green (#2E7D32) | Total value of all deals |
| Avg Win Probability | Average of win_probability | Orange (#F57C00) | Average across all opps |
| Pending Actions | 30% of total (mock) | Red (#C62828) | Items needing attention |

### **Toolbar:**
| Element | Type | Options | Purpose |
|---------|------|---------|---------|
| Filters | Button | Toggle filter panel | Show/hide filters |
| Find | Input | Text search | Search by name/customer |
| List | Dropdown | All/My/Open/Closed | Filter opportunities |
| Refresh | Button | - | Reload data |
| Actions | Dropdown | (Future) | Role-specific actions |
| Create Opportunity | Button | - | Add new opportunity |

### **Filter Panel:**
| Filter | Options |
|--------|---------|
| Practice | All Practices, IAM, Cloud, Security |
| Region | All Regions, MEA, ASEAN, EMEA |
| Status | All Statuses, Committed, Forecast, Pipeline |
| Sales Stage | All Stages, PO Received, Proposal, Negotiation |

### **Table Columns (13):**
1. Win (%) - Badge
2. Opportunity Nbr
3. Name - Link
4. Owner
5. Practice
6. Status - Badge
7. Creation Date
8. Account
9. Account Owner
10. Amount - Currency
11. Estimated Billing
12. Sales Stage
13. Region

### **Actions Available:**
- Click row → Navigate to `/score/:id`
- Click name → Navigate to `/score/:id`
- Search by name/customer
- Filter by practice/region/status/stage
- Refresh data

---

## 📊 **2. MANAGEMENT DASHBOARD** (`/management/dashboard`)

### **Purpose:**
Executive view for portfolio management, strategic decisions, and final approvals.

### **Metrics Cards:**
| Metric | Calculation | Color | Description |
|--------|------------|-------|-------------|
| Total Opportunities | Count of all opps | Blue (#1976D2) | Portfolio size |
| Pipeline Value | Sum of all deal_value | Green (#2E7D32) | Total portfolio value |
| Avg Win Probability | Average of win_probability | Orange (#F57C00) | Portfolio health indicator |
| Pending Approvals | Count of opps needing approval | Red (#C62828) | Awaiting management review |

### **Additional Metrics (Future):**
| Metric | Calculation | Purpose |
|--------|------------|---------|
| High-Risk Opportunities | Count where risk > threshold | Risk management |
| This Month Approvals | Count approved this month | Activity tracking |
| Win Rate | (Won / Total) * 100 | Success metric |
| Avg Deal Size | Total value / Count | Deal quality |

### **Toolbar:**
| Element | Options | Purpose |
|---------|---------|---------|
| Filters | Practice, Region, Status, Stage, Value Range | Advanced filtering |
| View | All/High Value/Pending Initial/Pending Final/Approved | Predefined views |
| Refresh | - | Reload data |
| Export | Excel/PDF | Download reports |
| Actions | Approve Selected, Reject Selected, Bulk Assign | Bulk operations |

### **Table Columns (Same 13 + Additional):**
- All 13 standard columns
- **+ BQS Score** (if assessed)
- **+ Approval Status** (Pending Initial/Pending Final/Approved/Rejected)
- **+ Assigned Practice Head**
- **+ Assigned SA**

### **Actions Available:**
- **Initial Review:** Approve/Reject/Hold new opportunities
- **Final Approval:** Approve/Reject assessed opportunities
- **View Details:** See complete BQS assessment
- **Request Info:** Ask for more details
- **Bulk Actions:** Approve/reject multiple at once
- **Export:** Download filtered data

### **Special Features:**
- **Pending Initial Review Tab:** New opportunities from Oracle
- **Pending Final Approval Tab:** Completed assessments awaiting decision
- **Approved Tab:** Approved opportunities
- **Rejected Tab:** Rejected opportunities with reasons

---

## 📊 **3. PRACTICE HEAD DASHBOARD** (`/practice-head/dashboard`)

### **Purpose:**
Practice-level management, SA assignment, and assessment quality control.

### **Metrics Cards:**
| Metric | Calculation | Color | Description |
|--------|------------|-------|-------------|
| Total Opportunities | Count in practice | Blue (#1976D2) | Practice portfolio size |
| Pipeline Value | Sum of practice deal_value | Green (#2E7D32) | Practice portfolio value |
| Avg Win Probability | Average in practice | Orange (#F57C00) | Practice health |
| Unassigned | Count not assigned to SA | Red (#C62828) | Need assignment |

### **Additional Metrics:**
| Metric | Calculation | Purpose |
|--------|------------|---------|
| Pending Review | Count of submitted assessments | Workload indicator |
| Avg Assessment Time | Average days to complete | Efficiency metric |
| SA Utilization | Assigned opps per SA | Resource planning |
| Practice Win Rate | (Won / Total) * 100 | Practice performance |

### **Toolbar:**
| Element | Options | Purpose |
|---------|---------|---------|
| Filters | SA, Region, Status, Stage | Filter by SA/region |
| View | Unassigned/Assigned/Pending Review/Approved | Workflow views |
| Refresh | - | Reload data |
| Actions | Assign to SA, Bulk Assign, Review Assessment | Assignment actions |

### **Table Columns (13 + Additional):**
- All 13 standard columns
- **+ Assigned SA** (Name or "Unassigned")
- **+ Assessment Status** (Not Started/In Progress/Submitted/Approved)
- **+ Days Since Assignment**
- **+ BQS Score** (if assessed)

### **Actions Available:**
- **Assign to SA:** Select SA from dropdown, assign opportunity
- **Bulk Assign:** Assign multiple opportunities to one SA
- **Review Assessment:** View submitted assessment, approve/reject
- **Request Changes:** Send assessment back to SA with comments
- **View SA Workload:** See how many opps each SA has
- **Reassign:** Move opportunity from one SA to another

### **Special Features:**
- **Unassigned Tab:** Opportunities approved by management, not yet assigned
- **Assigned Tab:** Opportunities assigned to SAs, in progress
- **Pending Review Tab:** Assessments submitted by SAs, awaiting review
- **Approved Tab:** Assessments approved, sent to management
- **SA Performance View:** Table showing each SA's metrics

---

## 📊 **4. SOLUTION ARCHITECT DASHBOARD** (`/sa/dashboard`)

### **Purpose:**
Personal workload management, assessment tracking, and submission status.

### **Metrics Cards:**
| Metric | Calculation | Color | Description |
|--------|------------|-------|-------------|
| Total Assigned | Count assigned to me | Blue (#1976D2) | My workload |
| Pipeline Value | Sum of my deal_value | Green (#2E7D32) | My portfolio value |
| Avg Win Probability | Average of my opps | Orange (#F57C00) | My success rate |
| Pending Assessment | Count not yet assessed | Red (#C62828) | Need my action |

### **Additional Metrics:**
| Metric | Calculation | Purpose |
|--------|------------|---------|
| Submitted | Count submitted to PH | Completed work |
| Approved | Count approved by PH | Success metric |
| Changes Requested | Count sent back | Rework needed |
| Avg Assessment Time | My average days | Personal efficiency |

### **Toolbar:**
| Element | Options | Purpose |
|---------|---------|---------|
| Filters | Status, Region, Practice | Filter my opps |
| View | Not Started/In Progress/Submitted/Approved | Workflow views |
| Refresh | - | Reload data |
| Actions | Start Assessment, Continue Draft, Submit | Assessment actions |

### **Table Columns (13 + Additional):**
- All 13 standard columns
- **+ Assessment Status** (Not Started/Draft/Submitted/Approved/Changes Requested)
- **+ Days Since Assigned**
- **+ BQS Score** (if assessed)
- **+ Practice Head Feedback** (if any)
- **+ Last Updated**

### **Actions Available:**
- **Start Assessment:** Begin BQS assessment for opportunity
- **Continue Draft:** Resume saved assessment
- **Submit Assessment:** Send completed assessment to Practice Head
- **View Feedback:** See Practice Head comments
- **Revise Assessment:** Update based on feedback
- **View Details:** See opportunity details from Oracle

### **Special Features:**
- **Not Started Tab:** Newly assigned, no assessment yet
- **In Progress Tab:** Assessments saved as draft
- **Submitted Tab:** Assessments sent to Practice Head
- **Approved Tab:** Assessments approved by Practice Head
- **Changes Requested Tab:** Assessments sent back for revision

---

## 🔄 **Data Flow Across Dashboards**

```
Oracle CRM (New Opportunity)
        ↓
┌───────────────────────┐
│  MAIN DASHBOARD       │ ← Everyone sees it
│  (All opportunities)  │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ MANAGEMENT DASHBOARD  │ ← Step 1: Initial Review
│ "New Opportunities"   │
└───────────┬───────────┘
            │
       ✅ Approve
            ↓
┌───────────────────────┐
│ PRACTICE HEAD DASH    │ ← Step 2: Assign to SA
│ "Unassigned Opps"     │
└───────────┬───────────┘
            │
       Assign to SA
            ↓
┌───────────────────────┐
│ SOLUTION ARCHITECT    │ ← Step 3: Complete Assessment
│ "My Assigned Opps"    │
└───────────┬───────────┘
            │
       Submit Assessment
            ↓
┌───────────────────────┐
│ PRACTICE HEAD DASH    │ ← Step 4: Review Assessment
│ "Pending Review"      │
└───────────┬───────────┘
            │
       ✅ Approve
            ↓
┌───────────────────────┐
│ MANAGEMENT DASHBOARD  │ ← Step 5: Final Approval
│ "Pending Final"       │
└───────────┬───────────┘
            │
       ✅ Approve
            ↓
      EXECUTION
```

---

## 📊 **Dashboard Metrics Comparison**

| Dashboard | Metric 1 | Metric 2 | Metric 3 | Metric 4 |
|-----------|----------|----------|----------|----------|
| **Main** | Total Opps (All) | Pipeline (All) | Avg Win (All) | Pending Actions |
| **Management** | Total Opps (All) | Pipeline (All) | Avg Win (All) | Pending Approvals |
| **Practice Head** | Total Opps (Practice) | Pipeline (Practice) | Avg Win (Practice) | Unassigned |
| **Solution Architect** | Total Assigned (Me) | Pipeline (Me) | Avg Win (Me) | Pending Assessment |

---

## 🎯 **Actions Comparison**

| Dashboard | Primary Actions | Secondary Actions |
|-----------|----------------|-------------------|
| **Main** | View, Search, Filter | Refresh, Navigate |
| **Management** | Approve, Reject, Hold | Export, Bulk Actions, Request Info |
| **Practice Head** | Assign to SA, Review | Reassign, Request Changes, View SA Workload |
| **Solution Architect** | Start Assessment, Submit | Continue Draft, Revise, View Feedback |

---

## 📋 **Implementation Checklist**

### **Main Dashboard** (`/`)
- [x] Metrics cards (4)
- [x] Toolbar with filters
- [x] Filter panel
- [x] Data table (13 columns)
- [x] Search functionality
- [x] Refresh button
- [ ] Actions dropdown implementation

### **Management Dashboard** (`/management/dashboard`)
- [x] Metrics cards (4)
- [x] Toolbar with filters
- [x] Data table (13 columns)
- [ ] Initial Review tab
- [ ] Final Approval tab
- [ ] Approve/Reject actions
- [ ] Export functionality

### **Practice Head Dashboard** (`/practice-head/dashboard`)
- [ ] Metrics cards (4)
- [ ] Toolbar with filters
- [ ] Data table (13+ columns)
- [ ] Unassigned tab
- [ ] Pending Review tab
- [ ] Assign to SA functionality
- [ ] Review assessment functionality

### **Solution Architect Dashboard** (`/sa/dashboard`)
- [ ] Metrics cards (4)
- [ ] Toolbar with filters
- [ ] Data table (13+ columns)
- [ ] Not Started tab
- [ ] In Progress tab
- [ ] Submitted tab
- [ ] Start Assessment action
- [ ] Submit Assessment action

---

## 🚀 **Next Steps**

1. **Create Practice Head Dashboard:**
   - Copy Main Dashboard structure
   - Filter data by practice
   - Add "Assigned SA" column
   - Add "Assign to SA" action
   - Add tabs: Unassigned, Assigned, Pending Review

2. **Create Solution Architect Dashboard:**
   - Copy Main Dashboard structure
   - Filter data by assigned SA
   - Add "Assessment Status" column
   - Add "Start Assessment" action
   - Add tabs: Not Started, In Progress, Submitted

3. **Enhance Management Dashboard:**
   - Add Initial Review tab
   - Add Final Approval tab
   - Add Approve/Reject buttons
   - Add Export functionality

4. **Connect Workflows:**
   - Link Management approval → Practice Head unassigned
   - Link Practice Head assign → SA dashboard
   - Link SA submit → Practice Head pending review
   - Link Practice Head approve → Management final approval

---

**This tabular summary defines all four dashboards and their requirements!** 📊
