# Bid Governance & Execution Dashboard - Implementation Specification

## Overview
This dashboard tracks opportunities through an 8-stage governance pipeline, providing real-time visibility into bid progression, governance status, and stuck opportunities requiring immediate attention.

---

## 1. Top-Level KPIs (Dashboard Header)

### Key Metrics to Display:
1. **Total Pipeline Value** - Sum of all opportunity deal values across all stages
2. **Weighted Revenue** - Pipeline value × win probability (aggregated)
3. **Avg Cycle Time** - Average time opportunities spend from Inbox to Closure
4. **Stuck Opportunities** - Count of opportunities >48hrs in critical stages (Evaluation, Governance Review)
5. **Governance Approval Rate** - % of opportunities approved vs rejected at Governance Review stage

### Visual Treatment:
- Large numeric display with trend indicators (↑↓)
- Color coding: Green (healthy), Yellow (warning), Red (critical)
- Compact cards in a horizontal row

---

## 2. The 8-Stage Workflow

### Stage Definitions:

1. **Inbox/Screening**
   - Initial Management approval
   - Pending with: Management Team

2. **Stakeholder Assignment**
   - Shared with Sales/Practice Heads
   - Pending with: Sales Head

3. **CRM Qualification**
   - Validated entry & Owner assignment
   - Pending with: CRM Admin

4. **Evaluation Cycle** ⚠ *Critical Stage*
   - Scoring, Win Probability, Budget alignment
   - Pending with: Solution Architect / Practice Head
   - **Alert Trigger**: >48 hours

5. **Feasibility/Due Diligence**
   - RFP analysis, Resource check, Financial validation
   - Pending with: Finance Team / Practice Head

6. **Governance Review** ⚠ *Critical Stage*
   - Leadership Go/No-Go decision
   - Pending with: Leadership / Governance Board
   - **Alert Trigger**: >48 hours

7. **Solutioning**
   - Requirements gathering, Design, Prototyping
   - Pending with: Solution Architect

8. **Closure**
   - Proposal submission, Negotiation, Contract Signing
   - Pending with: Sales Head / Legal

---

## 3. Funnel Visualization

### Recommended Approach:
**Horizontal Funnel Chart** showing drop-off rates between stages

```
Inbox (100) ──┐
              ├─→ Stakeholder (95) ──┐
              │                       ├─→ CRM (90) ──┐
              │                       │               ├─→ Evaluation (75) ──┐
              │                       │               │                      ├─→ ...
```

### Key Features:
- Width represents number of opportunities
- Color gradient from blue (early) to green (late stages)
- Click-through to filter table by stage
- Conversion rate % displayed between stages

### Alternative: Sankey Diagram
Shows flow including rejected/on-hold branches

---

## 4. Stage-Gate Alert System

### Critical Stage Monitoring (Evaluation & Governance Review)

#### Widget Design:
**"Stuck Opportunities" Alert Panel**

```
┌─────────────────────────────────────────┐
│ ⚠ STUCK OPPORTUNITIES (>48hrs)          │
├─────────────────────────────────────────┤
│ Evaluation Cycle:           3 stuck     │
│ Governance Review:          2 stuck     │
├─────────────────────────────────────────┤
│ [View All Stuck Items →]                │
└─────────────────────────────────────────┘
```

#### Visual Indicators:
- **Red badge** on Governance tab showing stuck count
- **Red row highlighting** in table for stuck opportunities
- **⚠ Icon** in "Stage Duration" column
- **Bold red text** for hours in stage

#### Alert Logic:
```typescript
const isStuck = (opp: Opportunity) => {
    const criticalStages = ['Evaluation Cycle', 'Governance Review'];
    const hoursInStage = calculateStageHours(opp.stage_entered_at);
    return criticalStages.includes(opp.current_stage || '') && hoursInStage > 48;
};
```

---

## 5. Action Center (List View)

### Table Columns:
1. **Checkbox** - Bulk selection
2. **Opp ID** - Clickable link to details
3. **Name/Customer** - Two-line display
4. **Practice** - Business unit
5. **Deal Size** - Formatted currency
6. **Win Prob** - Percentage
7. **Current Stage** - Badge with color coding
8. **Governance Status** - Color-coded badge:
   - 🟢 Approved (green)
   - 🔴 Rejected (red)
   - 🟡 On-Hold (yellow)
   - 🟠 Pending (orange)
9. **Pending With** - Role/Person responsible
10. **Stage Duration** - Hours in current stage (red if stuck)
11. **Actions** - Dropdown menu

### Action Menu Items:
- View Details
- Assign Stakeholder
- Start Assessment
- ─────────────
- Move to Next Stage
- Update Governance Status
- ─────────────
- Delete (red text)

### Tab Navigation:
- **All** - Complete pipeline view
- **Inbox** - Stages 1-3 (Screening, Assignment, Qualification)
- **Evaluation** - Stage 4 (Evaluation Cycle)
- **Governance** - Stages 5-6 (Feasibility, Governance Review) + stuck alert badge
- **Solutioning** - Stages 7-8 (Solutioning, Closure)

---

## 6. Data Structure (Database Schema)

### Opportunity Table - New Governance Fields:

```sql
-- Core fields (existing)
id, remote_id, name, customer, practice, geo, 
deal_value, currency, win_probability, sales_owner, 
stage, close_date, rfp_date, last_updated_in_crm, last_synced_at

-- Governance workflow fields (NEW)
current_stage           VARCHAR   DEFAULT 'Inbox/Screening'
governance_status       VARCHAR   DEFAULT 'Pending'  
stage_entered_at        TIMESTAMP DEFAULT NOW()
pending_with            VARCHAR   -- Role/Person who needs to act
budget_alignment        VARCHAR   -- 'Aligned', 'Misaligned', 'Under Review'
feasibility_status      VARCHAR   -- 'Not Started', 'In Progress', 'Completed'
solutioning_status      VARCHAR   -- 'Not Started', 'In Progress', 'Completed'
```

### TypeScript Interface:

```typescript
export interface Opportunity {
    // ... existing fields ...
    
    // Governance fields
    current_stage?: string;
    governance_status?: string;
    stage_entered_at?: string;
    pending_with?: string;
    budget_alignment?: string;
    feasibility_status?: string;
    solutioning_status?: string;
}
```

---

## 7. API Endpoints

### Existing:
- `GET /api/opportunities` - Fetch all opportunities
- `GET /api/oracle-opportunity/{id}` - Fetch single opportunity
- `POST /api/opportunities/{id}/assign` - Assign stakeholder

### New Governance Endpoints:

#### Move to Next Stage
```
POST /api/opportunities/{id}/move-stage
Body: {
    "stage": "Evaluation Cycle",
    "pending_with": "John Doe - Solution Architect"
}
```

#### Update Governance Status
```
POST /api/opportunities/{id}/governance-status
Body: {
    "status": "Approved" | "Rejected" | "On-Hold" | "Pending"
}
```

---

## 8. Implementation Checklist

### Backend ✅
- [x] Extended `Opportunity` model with governance fields
- [x] Created migration for new columns
- [x] Added `/move-stage` endpoint
- [x] Added `/governance-status` endpoint
- [x] Auto-advance logic (Approved → Solutioning)

### Frontend ✅
- [x] Updated TypeScript types
- [x] Changed tabs from assignment-based to stage-based
- [x] Added stuck opportunity detection logic
- [x] Updated table columns to show governance data
- [x] Added visual indicators (badges, colors, alerts)
- [x] Updated action menu with governance actions
- [x] Added stuck count badge on Governance tab
- [x] Implemented row highlighting for stuck items

### Pending (Future Enhancements)
- [ ] Top-level KPI cards component
- [ ] Funnel visualization chart
- [ ] Stuck opportunities alert panel widget
- [ ] Bulk actions (move multiple to next stage)
- [ ] Email notifications for stuck opportunities
- [ ] Stage transition history/audit log
- [ ] Dashboard export to PDF/Excel

---

## 9. Color Palette & Visual Design

### Stage Badges:
- All stages: `bg-blue-100 text-blue-800`

### Governance Status Badges:
- Approved: `bg-green-100 text-green-800`
- Rejected: `bg-red-100 text-red-800`
- On-Hold: `bg-yellow-100 text-yellow-800`
- Pending: `bg-orange-100 text-orange-800`

### Alert States:
- Stuck rows: `bg-red-50`
- Stuck duration text: `text-red-600 font-semibold`
- Alert badge: `bg-red-500 text-white`

---

## 10. User Roles & Permissions (Future)

| Role | View | Assign | Move Stage | Governance Decision |
|------|------|--------|------------|---------------------|
| Leadership | All | ✓ | ✓ | ✓ |
| Sales Head | All | ✓ | ✓ | ✗ |
| Bid Manager | All | ✓ | ✓ | ✗ |
| Solution Architect | Assigned | ✗ | ✗ | ✗ |

---

## Summary

This dashboard provides a complete governance tracking system with:
- **5 tabs** organizing opportunities by workflow stage
- **11 data columns** showing critical governance metrics
- **Automatic alerts** for opportunities stuck >48hrs in critical stages
- **Visual indicators** (color-coded badges, row highlighting, alert badges)
- **Action menu** with 7 governance-specific operations
- **Backend API** supporting stage transitions and status updates

The implementation maintains the existing visual template while adapting all functionality to the 8-stage Bid Governance & Execution workflow.
