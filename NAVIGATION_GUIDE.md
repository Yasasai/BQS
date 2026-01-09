# Navigation Implementation - Opportunity Inbox to Assigned to Me

## Overview
Successfully linked the **Opportunity Inbox** page to the **Assigned to Me** page with full navigation functionality. Both pages have unique designs while maintaining consistent actions based on the reference images.

## Pages Created

### 1. **Opportunity Inbox** (`/`)
**Design Features:**
- Tab navigation: Unassigned, Assigned, Needs Re-score
- Four filter dropdowns: Geo, Practice, Deal Size, Age
- Action buttons: Sync Opportunities, New Opportunity, More Actions
- Table columns: Opp ID, Name/Customer, Practice, Deal Size, Age, Owner, Score Status, Last Updated, Actions
- Row-level action menu with navigation

**Key Actions:**
- **View Details** → Navigates to `/assigned-to-me`
- **Start Assessment** → Navigates to `/assigned-to-me`
- **Assign Owner** → Placeholder for modal
- **Delete** → Placeholder for confirmation

### 2. **Assigned to Me** (`/assigned-to-me`)
**Design Features:**
- Status tabs: All, Not Started, Draft, Submitted
- Three filter dropdowns: All Practices, All Geos, All Values
- Table columns: Opp ID, Customer, Name, Practice, Value, Win %, Assessment Score, Score Status, Last Scored By
- Color-coded status badges:
  - **Submitted** → Green badge
  - **Draft** → Yellow badge
  - **Not Started** → Gray badge
- Pagination controls
- Back navigation to Opportunity Inbox

**Key Actions:**
- **Row Click** → Navigate to assessment detail (placeholder)
- **Back Button** → Returns to Opportunity Inbox
- **Filter Changes** → Client-side filtering

## Navigation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         TopBar                               │
│  [Opportunity Inbox]  [Assigned to Me]  (Active highlighting)│
└─────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
        ┌───────────────────┐  ┌──────────────────────┐
        │ Opportunity Inbox │  │   Assigned to Me     │
        │        (/)        │  │  (/assigned-to-me)   │
        └───────────────────┘  └──────────────────────┘
                    │                    │
                    │  View Details      │
                    │  Start Assessment  │
                    └───────────►────────┘
                                         │
                                         │ Back Button
                                         │
                                         ▼
                            ┌───────────────────┐
                            │ Opportunity Inbox │
                            └───────────────────┘
```

## Implementation Details

### Routing Setup
**File:** `frontend/src/App.tsx`
```tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { AssignedToMe } from './pages/AssignedToMe';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<OpportunityInbox />} />
                <Route path="/assigned-to-me" element={<AssignedToMe />} />
            </Routes>
        </Router>
    );
}
```

### TopBar Navigation
**File:** `frontend/src/components/TopBar.tsx`
- Added `Link` components from react-router-dom
- Active state highlighting based on current route
- Icons for visual clarity (Inbox, ClipboardCheck)

**Features:**
```tsx
<Link to="/" className={location.pathname === '/' ? 'active' : ''}>
    <Inbox size={16} /> Opportunity Inbox
</Link>
<Link to="/assigned-to-me" className={location.pathname === '/assigned-to-me' ? 'active' : ''}>
    <ClipboardCheck size={16} /> Assigned to Me
</Link>
```

### Action Menu Navigation
**File:** `frontend/src/pages/OpportunityInbox.tsx`

**View Details Button:**
```tsx
<button onClick={() => navigate('/assigned-to-me')}>
    View Details
</button>
```

**Start Assessment Button:**
```tsx
<button onClick={() => navigate('/assigned-to-me')}>
    Start Assessment
</button>
```

### Back Navigation
**File:** `frontend/src/pages/AssignedToMe.tsx`

**Back Button:**
```tsx
<button onClick={() => navigate('/')}>
    <ChevronLeft size={16} /> Back to Opportunity Inbox
</button>
```

## Unique Design Elements

### Opportunity Inbox
- **Color Scheme:** Gray-scale with blue accents
- **Layout:** Filter section with gray background
- **Status Badges:** Orange for unassigned/assigned
- **Table Style:** Clean, minimal borders
- **Hover Effect:** Light blue background on row hover

### Assigned to Me
- **Color Scheme:** Blue primary with status-based colors
- **Layout:** Compact header with inline filters
- **Status Badges:** 
  - Green (Submitted)
  - Yellow (Draft)
  - Gray (Not Started)
- **Table Style:** Professional with clear headers
- **Hover Effect:** Blue background on row hover
- **Additional:** Pagination controls at bottom

## Data Flow

### Opportunity Inbox
1. Fetches all opportunities from `/api/opportunities`
2. Filters by tab (unassigned/assigned/needs-rescore)
3. Applies client-side filters (geo, practice, deal size, age)
4. Displays filtered results

### Assigned to Me
1. Fetches all opportunities from `/api/opportunities`
2. Filters only assigned opportunities (has sales_owner)
3. Adds mock assessment status (in production, fetch from assessments table)
4. Filters by status tab (all/not-started/draft/submitted)
5. Applies client-side filters (practice, geo, value)
6. Displays filtered results with pagination

## Mock Data Additions

For demonstration purposes, the **Assigned to Me** page adds mock assessment data:
```tsx
const withAssessments = assigned.map((opp: Opportunity) => ({
    ...opp,
    assessment_status: Math.random() > 0.5 ? 'submitted' : 
                     Math.random() > 0.5 ? 'draft' : 'not-started',
    score: Math.random() > 0.3 ? Math.floor(Math.random() * 40) + 60 : undefined,
    score_status: Math.random() > 0.5 ? 'Submitted' : 
                Math.random() > 0.5 ? 'Draft' : 'Not Started',
    scored_by: opp.sales_owner
}));
```

**Note:** In production, replace this with actual API calls to fetch assessment data.

## Next Steps for Full Implementation

### 1. Backend API Endpoints
Create these endpoints to support the Assigned to Me page:

```python
@app.get("/api/assessments/{opp_id}")
def get_assessment(opp_id: int, db: Session = Depends(get_db)):
    """Get assessment details for an opportunity"""
    pass

@app.post("/api/assessments")
def create_assessment(assessment_data: dict, db: Session = Depends(get_db)):
    """Create or update an assessment"""
    pass

@app.get("/api/assigned-opportunities")
def get_assigned_opportunities(db: Session = Depends(get_db)):
    """Get opportunities assigned to current user with assessment status"""
    pass
```

### 2. Assessment Detail Page
Create a new page for detailed assessment view:
- **Route:** `/assessment/:id`
- **Features:**
  - Full opportunity details
  - Assessment form with scoring criteria
  - Save as draft functionality
  - Submit assessment functionality
  - Attachment upload
  - Comments section

### 3. User Authentication
- Implement user login/logout
- Filter "Assigned to Me" by current user
- Show only relevant opportunities

### 4. Real-time Updates
- WebSocket integration for live sync status
- Auto-refresh when new opportunities are synced
- Notification system for new assignments

### 5. Enhanced Filtering
- Implement server-side pagination
- Add search functionality
- Save filter preferences
- Export filtered results

### 6. Modals and Forms
- **Assign Owner Modal:** Dropdown to select owner
- **New Opportunity Modal:** Form to create opportunity
- **Delete Confirmation:** Confirm before deletion

## Testing Checklist

- [x] Navigation from Opportunity Inbox to Assigned to Me works
- [x] Back button returns to Opportunity Inbox
- [x] TopBar navigation highlights active page
- [x] Action menu "View Details" navigates correctly
- [x] Action menu "Start Assessment" navigates correctly
- [x] Tabs filter opportunities correctly
- [x] Filters update displayed data
- [x] Status badges display with correct colors
- [x] Both pages maintain unique visual design
- [ ] Assessment detail page navigation (pending implementation)
- [ ] Real backend integration for assessment data
- [ ] User-specific filtering

## File Structure

```
frontend/src/
├── App.tsx                          (Router setup)
├── components/
│   └── TopBar.tsx                   (Navigation bar with links)
├── pages/
│   ├── OpportunityInbox.tsx         (Main inbox page)
│   └── AssignedToMe.tsx             (Assigned opportunities page)
└── types.ts                         (TypeScript interfaces)

backend/
├── main.py                          (API endpoints)
├── database.py                      (DB models)
└── sync_manager.py                  (Oracle sync)
```

## Dependencies Installed

```json
{
  "react-router-dom": "^6.x.x"  // For routing functionality
}
```

## Running the Application

1. **Start Backend:**
   ```bash
   cd backend
   python main.py
   ```
   Backend runs on: http://localhost:8000

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on: http://localhost:5174

3. **Navigate:**
   - Main Inbox: http://localhost:5174/
   - Assigned to Me: http://localhost:5174/assigned-to-me

## Key Differences Between Pages

| Feature | Opportunity Inbox | Assigned to Me |
|---------|------------------|----------------|
| **Purpose** | Manage all opportunities | View assigned opportunities with assessments |
| **Tabs** | Unassigned, Assigned, Needs Re-score | All, Not Started, Draft, Submitted |
| **Filters** | Geo, Practice, Deal Size, Age | Practice, Geo, Value |
| **Table Focus** | Opportunity details | Assessment status and scores |
| **Actions** | Assign, View, Start Assessment, Delete | View details (row click) |
| **Status Badges** | Orange (Unassigned/Assigned) | Green/Yellow/Gray (Submitted/Draft/Not Started) |
| **Pagination** | Not implemented | Visible with controls |
| **Back Button** | None | Yes (to Opportunity Inbox) |

## Summary

✅ **Completed:**
- Full routing setup with react-router-dom
- Two distinct pages with unique designs
- Navigation between pages via TopBar and action menus
- Back navigation from Assigned to Me
- Client-side filtering on both pages
- Status-based visual indicators
- Mock assessment data for demonstration

🔄 **In Progress:**
- Backend API for assessment data
- Assessment detail page
- User authentication

📋 **Pending:**
- Real-time sync updates
- Server-side pagination
- Modal forms for actions
- Export functionality
