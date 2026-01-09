# Dashboard Actions Quick Reference

## OpportunityInbox.tsx - Sales Lead Dashboard

### Action Menu (Three-Dot Menu ⋯)

Each opportunity row has an action menu with the following options:

```
┌─────────────────────────┐
│  View Details           │  ← Navigate to opportunity detail page
├─────────────────────────┤
│  Assign Owner           │  ← Opens modal to assign Solution Architect
├─────────────────────────┤
│  Start Assessment       │  ← Navigate to scoring page
├─────────────────────────┤
│  Delete                 │  ← Delete the opportunity (red text)
└─────────────────────────┘
```

### Implementation Details

**Location**: Lines 343-369 in `OpportunityInbox.tsx`

**Code Structure**:
```typescript
{openActionMenu === opp.id && (
  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
    <div className="py-1">
      {/* 1. View Details */}
      <button onClick={() => navigate(`/opportunity/${opp.id}`)}>
        View Details
      </button>
      
      {/* 2. Assign Owner - Assigns to Solution Architect */}
      <button onClick={() => handleOpenAssignModal(opp.id)}>
        Assign Owner
      </button>
      
      {/* 3. Start Assessment */}
      <button onClick={() => navigate(`/score/${opp.id}`)}>
        Start Assessment
      </button>
      
      {/* 4. Delete */}
      <button className="text-red-600">
        Delete
      </button>
    </div>
  </div>
)}
```

### What "Assign Owner" Does

1. **Opens Modal**: `AssignArchitectModal` component
2. **User Selects**:
   - Primary SA (Solution Architect) from dropdown
   - CC Practice Head (optional text field)
   - Notes to SA (optional textarea)
3. **API Call**: `POST /api/opportunities/{id}/assign`
4. **Database Update**: Updates `sales_owner` field with Primary SA name
5. **Result**: Opportunity is now assigned to the selected Solution Architect

### Tabs in OpportunityInbox

```
┌──────────────┬──────────────┬──────────────────┐
│ Unassigned   │ Assigned     │ Needs Re-score   │
└──────────────┴──────────────┴──────────────────┘
```

- **Unassigned**: Opportunities without a `sales_owner` (or `sales_owner = 'N/A'`)
- **Assigned**: Opportunities with a `sales_owner` assigned
- **Needs Re-score**: Opportunities requiring reassessment (placeholder)

## PracticeHeadReview.tsx - Practice Head Dashboard

### Bulk Assignment Workflow

Instead of individual action menus, Practice Head uses **bulk selection**:

```
┌─────────────────────────────────────────────────┐
│  ☑ Select All                                   │
├─────────────────────────────────────────────────┤
│  ☑ Cloud Migration - ACME Corp                  │
│  ☑ Cybersecurity Assessment - TechStart         │
│  ☐ ERP Implementation - GlobalTech              │
└─────────────────────────────────────────────────┘

         ↓

   [Assign 2 to SA]  ← Button appears when items selected
```

### Tabs in PracticeHeadReview

```
┌──────────────┬──────────────┐
│ Unassigned   │ Assigned     │
└──────────────┴──────────────┘
```

- **Unassigned**: Opportunities awaiting SA assignment (bulk selection)
- **Assigned**: Submitted assessments from SAs for review

## AssignedToMe.tsx - Solution Architect Dashboard

### No Assignment Actions

Solution Architects **receive** assignments, they don't assign:

```
┌─────────────────────────────────────────────────┐
│  Action Column:                                 │
│  • [Score Now] - for Not Started/Draft          │
│  • [Submit to Practice Head] - for Submitted    │
└─────────────────────────────────────────────────┘
```

### Tabs in AssignedToMe

```
┌──────┬──────────────┬───────┬───────────┐
│ All  │ Not Started  │ Draft │ Submitted │
└──────┴──────────────┴───────┴───────────┘
```

## Role-Based Action Summary

| Role              | Dashboard           | Assignment Method    | Action Menu |
|-------------------|---------------------|----------------------|-------------|
| Sales Lead        | OpportunityInbox    | Individual (⋯ menu)  | ✅ Yes      |
| Practice Head     | PracticeHeadReview  | Bulk (checkboxes)    | ❌ No       |
| Solution Architect| AssignedToMe        | N/A (receives only)  | ❌ No       |

## Key Terminology

- **"Assign Owner"** = Assign to **Solution Architect**
- **"sales_owner"** field = Name of the assigned **Solution Architect**
- **"Primary SA"** = The main **Solution Architect** assigned to the opportunity
- **"CC Practice Head"** = Practice Head to be copied on the assignment

## Visual Reference

See the uploaded screenshot for the exact appearance of the action menu:
- Clean white dropdown
- Four options in order
- "Assign Owner" in regular text (not red)
- "Delete" in red text at the bottom
