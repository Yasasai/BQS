# Sales Lead Opportunity Inbox - Implementation Guide

## Overview
This document outlines the step-by-step implementation of the CRM-style opportunity inbox matching the reference design.

## Features Implemented

### 1. **Tab Navigation System**
- **Unassigned Tab**: Shows opportunities without an assigned sales owner
- **Assigned Tab**: Shows opportunities with assigned sales owners
- **Needs Re-score Tab**: Placeholder for opportunities requiring reassessment
- Each tab displays a dynamic count of opportunities

**Implementation Details:**
```typescript
const [activeTab, setActiveTab] = useState<TabType>('unassigned');
const unassignedCount = opportunities.filter(o => !o.sales_owner || o.sales_owner === 'N/A').length;
const assignedCount = opportunities.filter(o => o.sales_owner && o.sales_owner !== 'N/A').length;
```

### 2. **Filter System**
Four filter dropdowns implemented:
- **Geo Filter**: All Geographies, North America, Europe, Asia Pacific, Latin America
- **Practice Filter**: All Practices, Cloud Infra, Digital Strategy, Cybersecurity, AI/ML
- **Deal Size Filter**: Any Deal Size, < $100K, $100K - $500K, $500K - $1M, > $1M
- **Age Filter**: Any Age, < 7 days, 7-30 days, 30-90 days, > 90 days

**Implementation Details:**
```typescript
const getFilteredOpportunities = () => {
    let filtered = opportunities;
    
    // Tab filtering
    if (activeTab === 'unassigned') {
        filtered = filtered.filter(o => !o.sales_owner || o.sales_owner === 'N/A');
    } else if (activeTab === 'assigned') {
        filtered = filtered.filter(o => o.sales_owner && o.sales_owner !== 'N/A');
    }
    
    // Geo filtering
    if (selectedGeo !== 'All Geographies') {
        filtered = filtered.filter(o => o.geo === selectedGeo);
    }
    
    // Practice filtering
    if (selectedPractice !== 'All Practices') {
        filtered = filtered.filter(o => o.practice === selectedPractice);
    }
    
    return filtered;
};
```

### 3. **Action Buttons**
Three primary action buttons:
- **Sync Opportunities**: Triggers backend sync with Oracle CRM
  - Shows loading state ("Syncing...")
  - Disabled during sync operation
  - Automatically refreshes data after sync
- **+ New Opportunity**: Creates a new opportunity (placeholder)
- **More Actions**: Dropdown for additional actions (placeholder)

**Implementation Details:**
```typescript
const handleSync = async () => {
    setSyncing(true);
    try {
        const response = await fetch('http://localhost:8000/api/sync-database', {
            method: 'POST',
        });
        const data = await response.json();
        console.log(data.message);
        
        // Refresh opportunities after sync
        setTimeout(() => {
            fetchOpportunities();
            setSyncing(false);
        }, 2000);
    } catch (err) {
        console.error("Sync failed", err);
        setSyncing(false);
    }
};
```

### 4. **Enhanced Table Structure**
Updated columns to match CRM design:
1. **Checkbox**: For bulk selection
2. **Opp ID**: Displays remote_id or generated ID (OPP-{id})
3. **Name/Customer**: Two-line display with opportunity name and customer
4. **Practice**: Business unit/practice area
5. **Deal Size**: Formatted currency value
6. **Age**: Days since last sync (calculated dynamically)
7. **Owner**: Sales owner name or "N/A"
8. **Score Status**: Badge showing "Unassigned" or "Assigned"
9. **Last Updated**: Formatted date
10. **Actions**: Dropdown menu with row-level actions

**Implementation Details:**
```typescript
// Age calculation
const calculateAge = (lastSynced: string) => {
    const syncDate = new Date(lastSynced);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - syncDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
};
```

### 5. **Row-Level Actions Menu**
Each row has a dropdown menu with:
- **View Details**: Navigate to opportunity details
- **Assign Owner**: Assign a sales owner
- **Start Assessment**: Begin BQS assessment
- **Delete**: Remove opportunity (shown in red)

**Implementation Details:**
```typescript
const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);

// In the table row:
<button
    onClick={() => setOpenActionMenu(openActionMenu === opp.id ? null : opp.id)}
    className="text-gray-400 hover:text-gray-600"
>
    <MoreHorizontal size={18} />
</button>
{openActionMenu === opp.id && (
    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
        {/* Menu items */}
    </div>
)}
```

### 6. **Status Badges**
Color-coded badges for visual status indication:
- **Unassigned**: Orange badge (bg-orange-100 text-orange-800)
- **Assigned**: Orange badge (can be customized to green/blue)

### 7. **Dynamic Content Display**
- Results count updates based on active filters
- Contextual descriptions change based on active tab
- Empty states for loading and no results

## Backend Integration

### API Endpoints Used:
1. **GET /api/opportunities**: Fetches all opportunities
2. **POST /api/sync-database**: Triggers Oracle sync in background

### Data Flow:
```
1. Component mounts → fetchOpportunities()
2. User clicks "Sync Opportunities" → handleSync()
3. Backend processes sync → Background task
4. After 2 seconds → fetchOpportunities() (refresh data)
5. User changes filters → getFilteredOpportunities() (client-side filtering)
```

## Styling Approach
- Uses Tailwind CSS utility classes
- Follows modern CRM design patterns
- Gray-scale color scheme with blue accents
- Hover states for interactive elements
- Responsive table layout

## Next Steps for Full Implementation

### 1. **Connect Action Buttons**
- Implement "View Details" navigation
- Create "Assign Owner" modal/form
- Link "Start Assessment" to assessment flow
- Add confirmation dialog for "Delete"

### 2. **Enhance Filters**
- Add Deal Size range filtering logic
- Implement Age-based filtering
- Add search functionality
- Support multiple filter combinations

### 3. **Add Pagination**
- Implement server-side pagination
- Add page size selector
- Show total count and current page

### 4. **Implement Bulk Actions**
- Bulk assignment
- Bulk delete
- Export selected opportunities

### 5. **Real-time Updates**
- WebSocket integration for live sync status
- Auto-refresh on data changes
- Optimistic UI updates

### 6. **Assessment Integration**
- Link to assessment form
- Show assessment status in table
- Display scores in "Needs Re-score" tab

## Testing Checklist
- [ ] Tab switching works correctly
- [ ] Filters update the displayed opportunities
- [ ] Sync button triggers backend sync
- [ ] Action menu opens/closes properly
- [ ] Age calculation is accurate
- [ ] Status badges display correctly
- [ ] Empty states show when no data
- [ ] Loading states display during fetch

## File Structure
```
frontend/src/
├── pages/
│   └── OpportunityInbox.tsx (main implementation)
├── components/
│   └── TopBar.tsx (header component)
└── types.ts (TypeScript interfaces)

backend/
├── main.py (FastAPI endpoints)
├── database.py (DB models)
└── sync_manager.py (Oracle sync logic)
```

## Key State Variables
```typescript
- opportunities: Opportunity[]        // All opportunities from backend
- loading: boolean                    // Loading state
- activeTab: TabType                  // Current active tab
- syncing: boolean                    // Sync operation state
- selectedGeo: string                 // Geo filter value
- selectedPractice: string            // Practice filter value
- selectedDealSize: string            // Deal size filter value
- selectedAge: string                 // Age filter value
- openActionMenu: number | null       // Currently open action menu
```

## Performance Considerations
- Client-side filtering for fast response
- Debounce search inputs (when implemented)
- Lazy load large datasets
- Cache filter options
- Optimize re-renders with React.memo (if needed)
