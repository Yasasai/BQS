# Quick Start: Action Required Dashboard

## 🎯 What You Need to Know

The **Action Required** dashboard gives Practice Heads a single view of their two most important tasks:

### 1️⃣ Assign Opportunities to SAs
**What it shows**: Unassigned opportunities waiting for SA assignment

**What you do**: 
- Click "Assign" button
- Select a Solution Architect
- Done!

### 2️⃣ Approve or Reject Assessments
**What it shows**: Assessments submitted by SAs awaiting your review

**What you do**:
- ✅ Click green checkmark to approve
- ❌ Click red X to reject (with reason)
- 🔗 Click link icon to view full details first

## 🚀 How to Access

### Option 1: Sidebar Menu
1. Click hamburger menu (☰) in top-left
2. Look for "⚡ Action Required" at the top of Practice Head section
3. Click it

### Option 2: Direct URL
Navigate to: `http://localhost:5173/practice-head/action-required`

### Option 3: Default Landing
It's now your default landing page when you access the Practice Head dashboard!

## 📊 What You'll See

```
┌─────────────────────────────────────────────────────────────────┐
│                    Practice Head Dashboard                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────┐  ┌──────────────────────────┐   │
│  │ 1. Assign to SA          │  │ 2. Review & Approve      │   │
│  │ [Blue Header]            │  │ [Red Header]             │   │
│  │                          │  │                          │   │
│  │ • Opportunity 1          │  │ • Assessment 1           │   │
│  │   [Assign Button]        │  │   [✅] [❌] [🔗]        │   │
│  │                          │  │                          │   │
│  │ • Opportunity 2          │  │ • Assessment 2           │   │
│  │   [Assign Button]        │  │   [✅] [❌] [🔗]        │   │
│  │                          │  │                          │   │
│  │ View All (if >5) →       │  │ View All (if >5) →       │   │
│  └──────────────────────────┘  └──────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### Smart Counts
- See exactly how many items need your attention
- Large numbers in the header badges

### Quick Actions
- No need to open detail pages for simple tasks
- One-click assign, approve, or reject

### Empty States
- When everything is done, you'll see a friendly "All clear!" message
- Green checkmark indicates no pending work

### Overflow Handling
- Shows first 5 items in each category
- "View All" button appears if there are more

## 💡 Pro Tips

1. **Start Your Day Here**: Make this your morning landing page
2. **Clear Both Sides**: Aim to get both cards to zero
3. **Use Quick Actions**: For straightforward decisions
4. **View Details When Needed**: Click the link icon for complex assessments
5. **Refresh Often**: Click the refresh button to see latest updates

## 🔄 Workflow Example

### Assigning an Opportunity
```
1. See "Acme Corp Deal" in left card
2. Click "Assign" button
3. Select "John Smith (SA)" from dropdown
4. Click "Assign"
5. ✅ Opportunity disappears from this view
6. John receives the assignment
```

### Reviewing an Assessment
```
1. See "Beta Inc Assessment" in right card
2. Option A: Click ✅ to approve immediately
   OR
   Option B: Click 🔗 to view full assessment first
3. After review, click ✅ to approve or ❌ to reject
4. If rejecting, enter reason: "Please add more detail on risks"
5. ✅ Assessment moves to Approved/Rejected tab
6. SA receives notification
```

## 🆘 Quick Troubleshooting

**Problem**: Cards are empty but I know there are items
- **Solution**: Click the Refresh button (🔄) in the toolbar

**Problem**: Assign button doesn't work
- **Solution**: Make sure the SA exists in the system

**Problem**: Can't approve/reject
- **Solution**: Verify the assessment status is "SUBMITTED_FOR_REVIEW"

## 📱 Mobile Friendly

The dashboard automatically stacks vertically on smaller screens:
- Assignment card on top
- Review card below
- All functionality preserved

---

**Need Help?** Check the full documentation: [ACTION_REQUIRED_DASHBOARD.md](./ACTION_REQUIRED_DASHBOARD.md)

**Last Updated**: 2026-01-30
