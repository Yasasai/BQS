# Practice Head Action Required Dashboard

## Overview
The **Action Required** dashboard provides Practice Heads with a focused, streamlined view of the two most critical workflows that require their immediate attention:

1. **Unassigned Opportunities** - Opportunities that need to be assigned to Solution Architects
2. **Submitted Assessments** - Assessments that need to be approved or rejected

## Features

### 🎯 Two-Column Layout
The dashboard is organized into two side-by-side cards, each representing one critical workflow:

#### Left Card: Assign to Solution Architect
- **Purpose**: Shows opportunities awaiting SA assignment
- **Count Badge**: Displays the number of unassigned opportunities
- **Quick Actions**: 
  - Direct "Assign" button for each opportunity
  - Opens the SA assignment modal
  - Shows key opportunity details (deal value, win probability)
- **View More**: If more than 5 unassigned opportunities exist, a "View All" button appears

#### Right Card: Review & Approve/Reject
- **Purpose**: Shows assessments submitted by SAs awaiting PH review
- **Count Badge**: Displays the number of pending reviews
- **Quick Actions**:
  - ✅ **Approve** button (green) - Approves the assessment
  - ❌ **Reject** button (red) - Rejects with reason prompt
  - 🔗 **View Details** button (blue) - Opens full assessment view
- **View More**: If more than 5 pending reviews exist, a "View All" button appears

### 🎨 Visual Design
- **Color-Coded Headers**:
  - Blue gradient for assignment workflow
  - Red gradient for review workflow
- **Hover Effects**: Cards highlight on hover for better interactivity
- **Empty States**: Friendly messages when no action is required
- **Responsive**: Stacks vertically on smaller screens

### 🚀 Access Points

#### 1. Sidebar Navigation
- Located at the top of the "Practice Head" section
- Labeled as "⚡ Action Required"
- Icon: Alert circle to draw attention

#### 2. Direct URL
- Navigate to: `/practice-head/action-required`

#### 3. Default Landing Page
- When Practice Head logs in or navigates to their dashboard without a specific route, they land on this view by default

## Workflow Integration

### Workflow 1: Assignment Process
1. Practice Head sees unassigned opportunities in the left card
2. Clicks "Assign" button on an opportunity
3. Assignment modal opens with SA selection dropdown
4. Selects Primary SA (and optionally Secondary SA)
5. Clicks "Assign" to complete
6. Opportunity moves out of this view and into "Assigned to SA" status

### Workflow 2: Review Process
1. Solution Architect submits an assessment
2. Assessment appears in the right card with status "SUBMITTED_FOR_REVIEW"
3. Practice Head can:
   - **Quick Approve**: Click green checkmark for immediate approval
   - **Quick Reject**: Click red X, enter rejection reason
   - **Detailed Review**: Click blue link icon to view full assessment before deciding
4. After approval/rejection, assessment moves to appropriate tab (Approved/Rejected)

## Technical Details

### Frontend Components
- **File**: `frontend/src/pages/PracticeHeadDashboard.tsx`
- **Tab Type**: `'action-required'`
- **Route**: `/practice-head/action-required`

### State Management
- Uses existing `opportunities` state from API
- Filters in real-time based on workflow status
- Refreshes automatically after actions

### API Endpoints Used
- `GET /api/opportunities` - Fetches all opportunities
- `POST /api/inbox/assign` - Assigns opportunity to SA
- `POST /api/scoring/{opp_id}/review/approve` - Approves assessment
- `POST /api/scoring/{opp_id}/review/reject` - Rejects assessment

### Status Mapping
**Unassigned Opportunities**:
- `workflow_status` is NULL or not in finished states
- `assigned_sa` is NULL or "Unassigned"

**Submitted for Review**:
- `workflow_status` = "SUBMITTED_FOR_REVIEW"

## Benefits

### For Practice Heads
✅ **Single View**: Both critical workflows in one place
✅ **Quick Actions**: No need to navigate to detail pages for simple approvals
✅ **Clear Counts**: Immediately see pending workload
✅ **Prioritization**: Focus on what needs attention now

### For the Organization
✅ **Faster Turnaround**: Reduced clicks = faster decisions
✅ **Better Visibility**: Nothing falls through the cracks
✅ **Improved Workflow**: Clear separation of concerns
✅ **Audit Trail**: All actions still logged in backend

## Usage Tips

### Best Practices
1. **Check Daily**: Make this your landing page each morning
2. **Clear the Queue**: Try to keep both cards at zero
3. **Use Quick Actions**: For straightforward approvals/rejections
4. **View Details**: When you need more context before deciding
5. **Delegate Wisely**: Use the assignment feature to balance SA workloads

### Keyboard Shortcuts (Future Enhancement)
- `A` - Focus on assignment card
- `R` - Focus on review card
- `Tab` - Navigate between opportunities
- `Enter` - Open selected opportunity

## Troubleshooting

### "No opportunities showing"
- Check that backend is running
- Verify `workflow_status` is populated in database
- Run: `python backend/sync_workflow_status.py`

### "Assign button not working"
- Ensure SA email exists in system
- Check browser console for errors
- Verify backend API is accessible

### "Approve/Reject not working"
- Confirm opportunity status is "SUBMITTED_FOR_REVIEW"
- Check that you're logged in as Practice Head
- Verify backend endpoints are responding

## Future Enhancements

### Planned Features
- [ ] Bulk assignment (select multiple opportunities)
- [ ] Bulk approval (approve multiple assessments)
- [ ] Filtering by practice area
- [ ] Sorting by deal value, deadline, etc.
- [ ] Email notifications for new items
- [ ] SLA indicators (time since submission)
- [ ] Comments/notes on assignments
- [ ] Assignment history view

### Analytics Integration
- Track average time to assign
- Track average time to review
- Identify bottlenecks
- SA performance metrics

## Related Documentation
- [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md) - Complete workflow documentation
- [DASHBOARD_SYNC_GUIDE.md](./DASHBOARD_SYNC_GUIDE.md) - Data synchronization guide
- [COMPLETE_ROLE_SUMMARY.md](./COMPLETE_ROLE_SUMMARY.md) - Role-based access control

---

**Last Updated**: 2026-01-30
**Version**: 1.0
**Status**: ✅ Production Ready
