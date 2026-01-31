# 🎯 BQS Role-Based Workflow Summary

## Complete Overview of What Each Role Does

---

## 📊 **ROLE 1: MANAGEMENT**

### **Who They Are:**
- C-level executives
- Senior leadership
- Portfolio managers

### **What They See in Menu:**
```
┌─────────────────────────────┐
│  BQS Menu              [X]  │
├─────────────────────────────┤
│  Sarah Johnson              │
│  sarah.j@company.com        │
│  MANAGEMENT                 │
├─────────────────────────────┤
│  MANAGEMENT                 │
│  📊 Executive Dashboard     │
│  📈 Portfolio Analytics     │
│  ✅ Final Approvals         │
│  👥 Team Performance        │
├─────────────────────────────┤
│  GENERAL                    │
│  ⚙️  Settings                │
└─────────────────────────────┘
```

### **What They Do:**

#### **1. Executive Dashboard** (`/management/dashboard`)
**Purpose:** High-level overview of all opportunities

**What Happens:**
- See total pipeline value
- View win/loss ratio
- Monitor opportunities by stage
- Track revenue forecasts
- See practice-wise breakdown
- View regional performance

**Actions:**
- Filter by date range
- Drill down into specific practices
- Export reports
- View trends

**Data Shown:**
```
Total Opportunities: 150
Pipeline Value: $45M
Win Rate: 68%
High-Risk Opps: 12
Pending Approvals: 5
```

---

#### **2. Portfolio Analytics** (`/management/analytics`)
**Purpose:** Deep dive into portfolio health

**What Happens:**
- View detailed analytics
- Compare practices
- Analyze trends over time
- Identify bottlenecks
- Resource utilization metrics

**Actions:**
- Generate custom reports
- Compare time periods
- Export to Excel/PDF
- Set up alerts

**Data Shown:**
```
Revenue by Practice:
- IAM: $12M (27%)
- Cloud: $18M (40%)
- Security: $15M (33%)

Conversion Funnel:
Lead → Qualified → Assessed → Won
100  →    75     →    50    →  34
```

---

#### **3. Final Approvals** (`/management/approvals`)
**Purpose:** Approve/reject high-value opportunities

**What Happens:**
- See opportunities awaiting final approval
- Review complete BQS assessment
- View Practice Head recommendations
- See risk analysis
- Make go/no-go decision

**Actions:**
- ✅ Approve opportunity
- ❌ Reject opportunity
- 💬 Request more information
- 📝 Add executive comments

**Workflow:**
```
SA completes assessment
    ↓
Practice Head reviews & approves
    ↓
Management sees in "Final Approvals"
    ↓
Management reviews:
    - BQS Score
    - Risk factors
    - Resource requirements
    - Strategic fit
    ↓
Management approves/rejects
    ↓
Decision communicated to team
```

---

#### **4. Team Performance** (`/management/team`)
**Purpose:** Monitor team effectiveness

**What Happens:**
- View SA performance metrics
- See Practice Head effectiveness
- Track assessment quality
- Monitor turnaround times
- Identify top performers

**Actions:**
- View individual SA stats
- Compare practice performance
- Identify training needs
- Export performance reports

**Data Shown:**
```
Solution Architects:
- John Doe: 15 assessments, 85% win rate
- Jane Smith: 12 assessments, 72% win rate

Practice Heads:
- Mike Brown: 45 opps managed, 3.2 days avg review
- Lisa White: 38 opps managed, 2.8 days avg review
```

---

## 📋 **ROLE 2: PRACTICE HEAD**

### **Who They Are:**
- Practice leaders
- Domain experts
- Resource managers

### **What They See in Menu:**
```
┌─────────────────────────────┐
│  BQS Menu              [X]  │
├─────────────────────────────┤
│  Mike Brown                 │
│  mike.b@company.com         │
│  PRACTICE_HEAD              │
├─────────────────────────────┤
│  PRACTICE HEAD              │
│  📥 Unassigned Opps         │
│  ✓  Assign to SA            │
│  📄 Review Assessments      │
│  📊 Practice Metrics        │
├─────────────────────────────┤
│  GENERAL                    │
│  ⚙️  Settings                │
└─────────────────────────────┘
```

### **What They Do:**

#### **1. Unassigned Opportunities** (`/practice-head/unassigned`)
**Purpose:** View all opportunities not yet assigned to an SA

**What Happens:**
- See new opportunities from Oracle CRM
- Filter by practice, region, value
- View opportunity details
- Check SA availability
- Bulk assign capabilities

**Actions:**
- 👁️ View opportunity details
- ✓ Assign to SA
- 📊 Check SA workload
- 🔍 Filter/search

**Workflow:**
```
New opportunity synced from Oracle
    ↓
Appears in "Unassigned Opportunities"
    ↓
Practice Head sees:
    - Opportunity name
    - Customer
    - Value
    - Practice area
    - Region
    ↓
Practice Head assigns to SA based on:
    - SA expertise
    - Current workload
    - Availability
    - Past performance
```

**Data Shown:**
```
Unassigned Opportunities (23):

Opp #1902737 | IAM Implementation | $2.7M
Customer: Beta Information Technology
Region: MEA - Saudi Arabia
Practice: IAM - Cybertech
Status: New
[Assign to SA ▼]

Opp #1902738 | Cloud Migration | $1.5M
Customer: Acme Corp
Region: EMEA - UK
Practice: Cloud Services
Status: New
[Assign to SA ▼]
```

---

#### **2. Assign to SA** (`/practice-head/assign`)
**Purpose:** Assign opportunities to Solution Architects

**What Happens:**
- See list of SAs in practice
- View SA workload
- Match skills to opportunity
- Assign opportunity
- Notify SA

**Actions:**
- Select SA from dropdown
- View SA profile
- Check SA availability
- Assign opportunity
- Add assignment notes

**Workflow:**
```
Practice Head selects opportunity
    ↓
Views available SAs:
    - John Doe (3 active assessments)
    - Jane Smith (5 active assessments)
    ↓
Checks SA skills:
    - IAM expertise: ⭐⭐⭐⭐⭐
    - Cloud expertise: ⭐⭐⭐
    ↓
Assigns to best-fit SA
    ↓
SA receives notification
    ↓
Opportunity appears in SA's inbox
```

**Data Shown:**
```
Assign Opportunity #1902737

Available SAs:
┌──────────────┬────────┬───────────┬──────────┐
│ SA Name      │ Active │ Expertise │ Win Rate │
├──────────────┼────────┼───────────┼──────────┤
│ John Doe     │   3    │ IAM ⭐⭐⭐⭐⭐│   85%    │
│ Jane Smith   │   5    │ IAM ⭐⭐⭐  │   72%    │
│ Bob Johnson  │   2    │ IAM ⭐⭐⭐⭐ │   78%    │
└──────────────┴────────┴───────────┴──────────┘

[Select SA: John Doe ▼]
[Add Notes: _______________]
[Assign]
```

---

#### **3. Review Assessments** (`/practice-head/review`)
**Purpose:** Review completed assessments from SAs

**What Happens:**
- See submitted assessments
- Review BQS scores
- Check risk factors
- Validate assessment quality
- Approve or request changes

**Actions:**
- ✅ Approve assessment
- ↩️ Request changes
- 💬 Add comments
- 📊 View score breakdown
- 📝 Add practice-level insights

**Workflow:**
```
SA completes BQS assessment
    ↓
Submits to Practice Head
    ↓
Practice Head sees in "Review Assessments"
    ↓
Practice Head reviews:
    - Fit & Strategic Alignment: 85/100
    - Delivery Readiness: 72/100
    - Commercial Attractiveness: 90/100
    - Risk & Complexity: 65/100
    - Overall Score: 78/100
    ↓
Practice Head checks:
    - Are scores justified?
    - Are risks identified?
    - Is recommendation sound?
    ↓
Practice Head actions:
    - Approve → Goes to Management
    - Request changes → Back to SA
    - Add comments → Provide guidance
```

**Data Shown:**
```
Pending Reviews (8):

Opp #1902737 | IAM Implementation
Assessed by: John Doe
Submitted: 2 hours ago
Overall Score: 78/100
Recommendation: PURSUE

Scores:
- Fit & Strategic Alignment: 85/100 ⭐⭐⭐⭐
- Delivery Readiness: 72/100 ⭐⭐⭐
- Commercial Attractiveness: 90/100 ⭐⭐⭐⭐⭐
- Risk & Complexity: 65/100 ⭐⭐⭐

[View Full Assessment] [Approve] [Request Changes]
```

---

#### **4. Practice Metrics** (`/practice-head/metrics`)
**Purpose:** Monitor practice performance

**What Happens:**
- View practice-specific analytics
- Track SA performance
- Monitor win rates
- Identify trends
- Resource planning

**Actions:**
- Filter by date range
- Compare SAs
- Export reports
- View trends

**Data Shown:**
```
IAM Practice Metrics:

Total Opportunities: 45
Pipeline Value: $12M
Win Rate: 68%
Avg Assessment Time: 3.2 days

SA Performance:
- John Doe: 15 opps, 85% win rate
- Jane Smith: 12 opps, 72% win rate
- Bob Johnson: 18 opps, 78% win rate

Trends:
- Win rate up 5% this quarter
- Average deal size: $267K
- Most common risk: Resource availability
```

---

## 👨‍💻 **ROLE 3: SOLUTION ARCHITECT (SA)**

### **Who They Are:**
- Technical experts
- Solution designers
- Assessment specialists

### **What They See in Menu:**
```
┌─────────────────────────────┐
│  BQS Menu              [X]  │
├─────────────────────────────┤
│  John Doe                   │
│  john.doe@company.com       │
│  SA                         │
├─────────────────────────────┤
│  SOLUTION ARCHITECT         │
│  📥 My Assigned Opps        │
│  📄 Start Assessment        │
│  ✅ Submitted Assessments   │
├─────────────────────────────┤
│  GENERAL                    │
│  ⚙️  Settings                │
└─────────────────────────────┘
```

### **What They Do:**

#### **1. My Assigned Opportunities** (`/`)
**Purpose:** View opportunities assigned to me

**What Happens:**
- See all opportunities assigned by Practice Head
- Filter by status, date, value
- Quick access to start assessment
- Track assessment progress

**Actions:**
- 📄 Start assessment
- 👁️ View opportunity details
- 🔍 Filter/search
- 📊 Sort by priority

**Workflow:**
```
Practice Head assigns opportunity
    ↓
SA receives notification
    ↓
Opportunity appears in "My Assigned Opportunities"
    ↓
SA sees:
    - Opportunity details from Oracle
    - Customer information
    - Deal value
    - Timeline
    - Practice Head notes
    ↓
SA clicks "Start Assessment"
```

**Data Shown:**
```
My Assigned Opportunities (5):

┌────────┬──────────────────┬──────────┬────────┬──────────┐
│ Opp #  │ Name             │ Customer │ Value  │ Status   │
├────────┼──────────────────┼──────────┼────────┼──────────┤
│1902737 │ IAM Impl.        │ Beta IT  │ $2.7M  │ New      │
│1902738 │ Cloud Migration  │ Acme     │ $1.5M  │ Draft    │
│1902739 │ Security Audit   │ TechCo   │ $800K  │ Submitted│
└────────┴──────────────────┴──────────┴────────┴──────────┘

[Start Assessment] [View Details]
```

---

#### **2. Start Assessment** (`/sa/assess`)
**Purpose:** Complete BQS assessment for an opportunity

**What Happens:**
- Open assessment form
- Fill out 4 scoring sections
- Answer questions for each section
- Calculate scores
- Add comments
- Save draft or submit

**Actions:**
- 📝 Fill out assessment
- 💾 Save draft
- ✅ Submit to Practice Head
- 📊 View score calculation

**Workflow:**
```
SA clicks "Start Assessment"
    ↓
Assessment form opens with 4 sections:

1. Fit & Strategic Alignment
   - Does this align with our strategy?
   - Do we have the right expertise?
   - Is this a good customer fit?
   Score: __/100

2. Delivery Readiness
   - Do we have resources available?
   - Can we meet the timeline?
   - Do we have the technology?
   Score: __/100

3. Commercial Attractiveness
   - Is the margin acceptable?
   - Is the deal size right?
   - Are payment terms good?
   Score: __/100

4. Risk & Complexity
   - What are the risks?
   - How complex is delivery?
   - Are there dependencies?
   Score: __/100
    ↓
SA fills out each section
    ↓
System calculates overall score
    ↓
SA adds final recommendation:
    - PURSUE
    - PURSUE WITH CAUTION
    - DO NOT PURSUE
    ↓
SA submits to Practice Head
```

**Data Shown:**
```
BQS Assessment - Opp #1902737

Opportunity: IAM Implementation
Customer: Beta Information Technology
Value: $2.7M

Section 1: Fit & Strategic Alignment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q1: Strategic alignment? [⭐⭐⭐⭐⭐]
Q2: Expertise match?     [⭐⭐⭐⭐⭐]
Q3: Customer fit?        [⭐⭐⭐⭐]
Section Score: 85/100

Section 2: Delivery Readiness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q1: Resource availability? [⭐⭐⭐⭐]
Q2: Timeline feasible?     [⭐⭐⭐]
Q3: Technology ready?      [⭐⭐⭐⭐]
Section Score: 72/100

[Continue to Section 3...]

Overall Score: 78/100
Recommendation: [PURSUE ▼]

[Save Draft] [Submit to Practice Head]
```

---

#### **3. Submitted Assessments** (`/sa/submitted`)
**Purpose:** View all submitted assessments and their status

**What Happens:**
- See all assessments submitted to Practice Head
- Check review status
- View feedback
- Track approval progress

**Actions:**
- 👁️ View assessment
- 📝 View feedback
- 🔄 Resubmit if changes requested
- 📊 Track status

**Workflow:**
```
SA submits assessment
    ↓
Appears in "Submitted Assessments"
    ↓
Status: "Pending Practice Head Review"
    ↓
Practice Head reviews
    ↓
Status changes to:
    - "Approved" → Goes to Management
    - "Changes Requested" → SA can revise
    - "Rejected" → SA sees reason
    ↓
If approved by Management:
    - Status: "Final Approval Granted"
    - Opportunity moves to execution
```

**Data Shown:**
```
Submitted Assessments (12):

┌────────┬──────────────┬───────┬─────────────┬──────────┐
│ Opp #  │ Name         │ Score │ Status      │ Action   │
├────────┼──────────────┼───────┼─────────────┼──────────┤
│1902737 │ IAM Impl.    │ 78/100│ Pending PH  │ [View]   │
│1902738 │ Cloud Mig.   │ 85/100│ Approved    │ [View]   │
│1902739 │ Security     │ 65/100│ Changes Req │ [Revise] │
│1902740 │ Data Center  │ 92/100│ Final Appr. │ [View]   │
└────────┴──────────────┴───────┴─────────────┴──────────┘

Status Legend:
- Pending PH: Awaiting Practice Head review
- Approved: Practice Head approved, sent to Management
- Changes Req: Practice Head requested changes
- Final Appr.: Management approved, ready to execute
```

---

## 🔄 **COMPLETE WORKFLOW - All Roles Together**

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Opportunity Enters System                      │
└─────────────────────────────────────────────────────────┘
Oracle CRM → Auto-sync → PostgreSQL → BQS System
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Management Initial Review (MANAGEMENT ROLE)    │
│  ⭐ NEW: All opportunities go to Management first       │
└─────────────────────────────────────────────────────────┘
Management sees in "New Opportunities" dashboard
    ↓
Reviews opportunity:
    - Customer name
    - Deal value
    - Practice area
    - Strategic fit
    - Initial risk assessment
    ↓
Management decides:
    ✅ Approve for Assessment → Send to Practice Head
    ❌ Reject → Opportunity stopped (not strategic fit)
    ⏸️  Hold → Keep for later review
    💬 Request info → Get more details first
    ↓
If approved, Management assigns to Practice Head
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Practice Head Assigns (PRACTICE HEAD ROLE)     │
└─────────────────────────────────────────────────────────┘
Practice Head sees in "Unassigned Opportunities"
(Only opportunities approved by Management)
    ↓
Reviews opportunity details
    ↓
Checks SA availability & expertise
    ↓
Assigns to best-fit SA
    ↓
SA receives notification
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 4: SA Assesses (SOLUTION ARCHITECT ROLE)          │
└─────────────────────────────────────────────────────────┘
SA sees in "My Assigned Opportunities"
    ↓
Clicks "Start Assessment"
    ↓
Fills out 4 sections:
    - Fit & Strategic Alignment
    - Delivery Readiness
    - Commercial Attractiveness
    - Risk & Complexity
    ↓
System calculates overall score
    ↓
SA adds recommendation (PURSUE/CAUTION/NO)
    ↓
Submits to Practice Head
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 5: Practice Head Reviews (PRACTICE HEAD ROLE)     │
└─────────────────────────────────────────────────────────┘
Practice Head sees in "Review Assessments"
    ↓
Reviews:
    - All section scores
    - Risk factors
    - SA recommendation
    - Supporting comments
    ↓
Practice Head decides:
    ✅ Approve → Sends to Management for Final Approval
    ↩️ Request changes → Back to SA
    ❌ Reject → Provide reason
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 6: Management Final Approval (MANAGEMENT ROLE)    │
└─────────────────────────────────────────────────────────┘
Management sees in "Final Approvals"
    ↓
Reviews complete assessment:
    - BQS score
    - Practice Head recommendation
    - Risk analysis
    - Strategic fit
    - Resource requirements
    ↓
Management decides:
    ✅ Approve → Opportunity proceeds to execution
    ❌ Reject → Opportunity stopped
    💬 Request info → Back to Practice Head
    ↩️ Send back to SA → Request reassessment
                                           ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 7: Execution (If Approved)                        │
└─────────────────────────────────────────────────────────┘
Opportunity marked as "Approved"
    ↓
Sales team proceeds with proposal
    ↓
Delivery team prepares resources
    ↓
All roles can track in their dashboards
```

---

## 🎯 **Updated Workflow Summary**

### **Management Touches Opportunity TWICE:**

1. **Initial Review (Step 2):**
   - Right after sync from Oracle
   - Quick strategic fit check
   - Approve/reject before assessment
   - **Purpose:** Filter out non-strategic opportunities early

2. **Final Approval (Step 6):**
   - After complete BQS assessment
   - Detailed review with scores
   - Final go/no-go decision
   - **Purpose:** Validate assessment and make final call

### **Why Management Reviews First:**

✅ **Strategic Alignment:** Ensure opportunity fits company strategy before investing time in assessment

✅ **Resource Efficiency:** Don't waste SA time on opportunities that won't be pursued

✅ **Early Risk Detection:** Identify deal-breakers early (wrong customer, wrong region, too small, etc.)

✅ **Portfolio Management:** Control which opportunities enter the pipeline

✅ **Quick Rejection:** Stop non-strategic deals immediately without full assessment

---

## 📊 **Updated Management Menu**

```
┌─────────────────────────────────┐
│  BQS Menu              [X]      │
├─────────────────────────────────┤
│  Sarah Johnson                  │
│  sarah.j@company.com            │
│  MANAGEMENT                     │
├─────────────────────────────────┤
│  MANAGEMENT                     │
│  📊 Executive Dashboard         │
│  📈 Portfolio Analytics         │
│  🆕 New Opportunities (Initial) │ ← NEW!
│  ✅ Final Approvals             │
│  👥 Team Performance            │
├─────────────────────────────────┤
│  GENERAL                        │
│  ⚙️  Settings                    │
└─────────────────────────────────┘
```

### **New Menu Item: "New Opportunities (Initial Review)"**

**Purpose:** Review all new opportunities from Oracle before sending to Practice Head

**What Management Sees:**
```
New Opportunities Awaiting Initial Review (15):

┌────────┬──────────────────┬──────────┬────────┬──────────┐
│ Opp #  │ Name             │ Customer │ Value  │ Practice │
├────────┼──────────────────┼──────────┼────────┼──────────┤
│1902737 │ IAM Impl.        │ Beta IT  │ $2.7M  │ IAM      │
│1902738 │ Cloud Migration  │ Acme     │ $1.5M  │ Cloud    │
│1902739 │ Security Audit   │ TechCo   │ $800K  │ Security │
└────────┴──────────────────┴──────────┴────────┴──────────┘

Actions for each:
[✅ Approve for Assessment] → Sends to Practice Head
[❌ Reject] → Stops opportunity
[⏸️ Hold] → Keep for later
[💬 Request Info] → Get more details
```

**Management Decision Criteria:**
- Is customer strategic?
- Is deal size acceptable?
- Does it fit our portfolio?
- Do we have capacity?
- Is region aligned with strategy?
- Are there any red flags?

---

## 🔄 **Visual Flow with Management First**

```
Oracle CRM (New Opportunity)
        ↓
    ┌───────┐
    │ SYNC  │
    └───┬───┘
        ↓
┌───────────────────┐
│   MANAGEMENT      │ ← FIRST REVIEW
│ Initial Review    │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ✅        ❌
Approve    Reject
    │         │
    │         └──→ STOPPED
    ↓
┌───────────────────┐
│  PRACTICE HEAD    │
│ Assign to SA      │
└────────┬──────────┘
         ↓
┌───────────────────┐
│ SOLUTION ARCHITECT│
│ Complete BQS      │
└────────┬──────────┘
         ↓
┌───────────────────┐
│  PRACTICE HEAD    │
│ Review Assessment │
└────────┬──────────┘
         ↓
┌───────────────────┐
│   MANAGEMENT      │ ← SECOND REVIEW
│ Final Approval    │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ✅        ❌
Approve    Reject
    │         │
    │         └──→ STOPPED
    ↓
┌───────────────────┐
│   EXECUTION       │
└───────────────────┘
```

---

## 📊 **Summary Table - What Each Role Does**

| Role | Main Responsibilities | Key Actions | Decision Power |
|------|----------------------|-------------|----------------|
| **MANAGEMENT** | Portfolio oversight, final approvals, strategy | View dashboards, approve/reject high-value opps, monitor team | ✅ Final go/no-go |
| **PRACTICE HEAD** | Resource allocation, quality control, practice management | Assign to SAs, review assessments, approve/reject | ✅ Approve assessments |
| **SOLUTION ARCHITECT** | Technical assessment, scoring, recommendations | Fill BQS assessment, score sections, recommend | 💡 Recommend only |

---

## 🎯 **Key Differences**

### **MANAGEMENT:**
- **Sees:** Everything (all practices, all opportunities)
- **Does:** Strategic decisions, final approvals
- **Focus:** Portfolio health, win rates, team performance

### **PRACTICE HEAD:**
- **Sees:** Their practice only
- **Does:** Assign work, review quality, manage resources
- **Focus:** Practice performance, SA effectiveness, assessment quality

### **SOLUTION ARCHITECT:**
- **Sees:** Their assigned opportunities only
- **Does:** Technical assessment, scoring, recommendations
- **Focus:** Opportunity viability, risk identification, accurate scoring

---

**This is your complete BQS role-based workflow! Each role has clear responsibilities and actions.** 🎉
