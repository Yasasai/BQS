# Assignment Logic & Dashboard Actions - Implementation Summary

## Overview
This document explains how the "Assign Owner" functionality works across different dashboards and how it assigns opportunities to Solution Architects.

## Assignment Flow

### 1. **Sales Lead (Opportunity Inbox)**
**Location**: `OpportunityInbox.tsx`

**User Flow**:
1. Sales Lead views opportunities in the Opportunity Inbox
2. Clicks the three-dot menu (⋯) next to an opportunity
3. Selects "Assign Owner" from the dropdown menu
4. A modal opens (`AssignArchitectModal.tsx`) with:
   - **Primary SA**: Dropdown to select a Solution Architect
   - **CC Practice Head**: Text field to specify the Practice Head to CC
   - **Notes to SA**: Optional textarea for instructions
5. Clicks "Assign" button
6. Backend API is called: `POST /api/opportunities/{id}/assign`
7. The `sales_owner` field in the database is updated with the Primary SA's name
8. Success message is displayed
9. Opportunities list is refreshed

**Action Menu Items** (in order):
- View Details
- **Assign Owner** ← Assigns to Solution Architect
- Start Assessment
- Delete

### 2. **Practice Head (Practice Head Review)**
**Location**: `PracticeHeadReview.tsx`

**User Flow** (Bulk Assignment):
1. Practice Head views the "Unassigned" tab
2. Selects multiple opportunities using checkboxes
3. Clicks "Assign {count} to SA" button at the top
4. A modal opens (similar to Sales Lead) to assign all selected opportunities
5. All selected opportunities are assigned to the chosen Solution Architect

**Tabs**:
- **Unassigned**: Opportunities awaiting SA assignment (bulk selection)
- **Assigned**: Submitted assessments from SAs for review

### 3. **Solution Architect (Assigned to Me)**
**Location**: `AssignedToMe.tsx`

**User Flow**:
1. Solution Architect views opportunities assigned to them
2. Can filter by status: All, Not Started, Draft, Submitted
3. Clicks "Score Now" or "Submit to Practice Head" buttons
4. No "Assign Owner" action here (they are the assigned owner)

## Backend Implementation

### API Endpoint
```python
POST /api/opportunities/{id}/assign
```

**Request Body**:
```json
{
  "primarySA": "Alice Johnson",
  "ccPracticeHead": "IT Services",
  "notes": "Please prioritize this opportunity"
}
```

**Response**:
```json
{
  "message": "Solution Architect assigned successfully",
  "opportunity_id": 123,
  "assigned_to": "Alice Johnson"
}
```

**Database Update**:
- Updates the `sales_owner` field in the `opportunities` table
- The `sales_owner` field stores the name of the assigned Solution Architect

## Dashboard Actions Alignment

### OpportunityInbox.tsx (Sales Lead)
✅ **Correctly Aligned** - Lines 343-369

```typescript
<div className="py-1">
  <button onClick={() => navigate(`/opportunity/${opp.id}`)}>
    View Details
  </button>
  <button onClick={() => handleOpenAssignModal(opp.id)}>
    Assign Owner  ← Assigns to Solution Architect
  </button>
  <button onClick={() => navigate(`/score/${opp.id}`)}>
    Start Assessment
  </button>
  <button className="text-red-600">
    Delete
  </button>
</div>
```

### AssignArchitectModal.tsx
✅ **Correctly Implemented** - Lines 76-81

```typescript
<h2>Assign Solution Architect</h2>
<p>
  Assign a primary Solution Architect and an optional CC Practice Head 
  to the selected opportunity.
</p>
```

### Backend main.py
✅ **Correctly Implemented** - Lines 73-98

```python
@app.post("/api/opportunities/{id}/assign")
def assign_solution_architect(id: int, assignment_data: dict, db: Session = Depends(get_db)):
    """
    Assign a Solution Architect to an opportunity.
    Updates the sales_owner field with the primary SA name.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Update the sales_owner with the primary SA
    opp.sales_owner = assignment_data.get("primarySA", "")
    
    db.commit()
    db.refresh(opp)
    
    return {
        "message": "Solution Architect assigned successfully",
        "opportunity_id": id,
        "assigned_to": opp.sales_owner
    }
```

## Key Points

1. **"Assign Owner" = Assign to Solution Architect**: The terminology is clear - when you click "Assign Owner", you are assigning a Solution Architect to the opportunity.

2. **sales_owner field**: This database field stores the name of the assigned Solution Architect.

3. **Consistent across dashboards**: The action menu in OpportunityInbox follows the exact order shown in your screenshot:
   - View Details
   - Assign Owner
   - Start Assessment
   - Delete

4. **Role-based workflows**:
   - **Sales Lead**: Individual assignment via action menu
   - **Practice Head**: Bulk assignment via checkboxes
   - **Solution Architect**: No assignment action (they receive assignments)

## Testing the Flow

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to Opportunity Inbox
4. Click the three-dot menu on any opportunity
5. Select "Assign Owner"
6. Choose a Solution Architect from the dropdown
7. Click "Assign"
8. Verify the opportunity now shows the assigned SA in the "Owner" column

## Database Schema

```python
class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    remote_id = Column(String, unique=True, index=True)
    name = Column(String)
    customer = Column(String)
    practice = Column(String)
    geo = Column(String)
    deal_value = Column(Float)
    currency = Column(String)
    win_probability = Column(Float)
    sales_owner = Column(String)  # ← Stores the assigned Solution Architect name
    stage = Column(String)
    close_date = Column(DateTime, nullable=True)
    rfp_date = Column(DateTime, nullable=True)
    last_updated_in_crm = Column(DateTime)
    last_synced_at = Column(DateTime, default=datetime.utcnow)
```

## Summary

✅ **Assignment Logic**: "Assign Owner" correctly assigns opportunities to Solution Architects by updating the `sales_owner` field.

✅ **Dashboard Actions**: The action menu in OpportunityInbox is properly aligned with your requirements:
   1. View Details
   2. Assign Owner (assigns to SA)
   3. Start Assessment
   4. Delete

✅ **Backend API**: The `/api/opportunities/{id}/assign` endpoint is implemented and functional.

✅ **Frontend Integration**: The OpportunityInbox component properly calls the backend API and handles the assignment flow.

All components are working together as designed!
