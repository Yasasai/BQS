# 🎯 Role-Based Navigation System

## Overview
Implemented a role-based sidebar menu that shows different options based on user roles: Management, Practice Head, and Solution Architect.

---

## 📋 What Was Created

### **1. RoleSidebar Component (`frontend/src/components/RoleSidebar.tsx`)**

**Features:**
- ✅ Slides in from left when hamburger menu is clicked
- ✅ Shows different menu items based on user role
- ✅ Displays user info (name, email, roles)
- ✅ Smooth animations
- ✅ Click outside to close
- ✅ Oracle-style design

---

## 🎯 Role-Based Menu Items

### **1. MANAGEMENT Role**

**Menu Items:**
1. **Executive Dashboard** - `/management/dashboard`
   - High-level overview of all opportunities
   - Portfolio health metrics
   - Win/loss analytics

2. **Portfolio Analytics** - `/management/analytics`
   - Detailed analytics and trends
   - Revenue forecasting
   - Practice performance comparison

3. **Final Approvals** - `/management/approvals`
   - Review and approve high-value opportunities
   - Final go/no-go decisions
   - Risk assessment review

4. **Team Performance** - `/management/team`
   - SA performance metrics
   - Practice Head effectiveness
   - Resource utilization

---

### **2. PRACTICE HEAD Role**

**Menu Items:**
1. **Unassigned Opportunities** - `/practice-head/unassigned`
   - View all opportunities not yet assigned to an SA
   - Filter by practice, region, value
   - Bulk assignment capabilities

2. **Assign to SA** - `/practice-head/assign`
   - Assign opportunities to Solution Architects
   - View SA workload
   - Match skills to opportunities

3. **Review Assessments** - `/practice-head/review`
   - Review completed assessments from SAs
   - Approve or request changes
   - Add practice-level comments

4. **Practice Metrics** - `/practice-head/metrics`
   - Practice-specific analytics
   - SA performance in practice
   - Win rate by practice

---

### **3. SOLUTION ARCHITECT Role**

**Menu Items:**
1. **My Assigned Opportunities** - `/`
   - View opportunities assigned to me
   - Filter by status, date, value
   - Quick access to start assessment

2. **Start Assessment** - `/sa/assess`
   - Begin BQS assessment for an opportunity
   - Fill out scoring sections
   - Save draft or submit

3. **Submitted Assessments** - `/sa/submitted`
   - View all submitted assessments
   - Check review status
   - View feedback from Practice Head

---

## 🔗 How It Links with Existing Logic

### **User Context Integration**

The sidebar uses the existing `UserContext` to:
```typescript
const { currentUser } = useUser();

// Check roles
const hasRole = (role: string) => currentUser?.roles?.includes(role);
const isManagement = hasRole('MANAGEMENT');
const isPracticeHead = hasRole('PRACTICE_HEAD');
const isSolutionArchitect = hasRole('SA');
```

### **Role Detection**

**From Backend (`backend/app/models.py`):**
```python
class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True)
    role_code = Column(String)  # 'MANAGEMENT', 'PRACTICE_HEAD', 'SA'
    role_name = Column(String)
```

**Frontend receives:**
```json
{
  "user_id": "1",
  "display_name": "John Doe",
  "email": "john@example.com",
  "roles": ["PRACTICE_HEAD", "SA"]
}
```

### **Navigation Flow**

```
User clicks hamburger menu
    ↓
Sidebar opens (RoleSidebar component)
    ↓
Checks currentUser.roles
    ↓
Shows relevant menu sections
    ↓
User clicks menu item
    ↓
navigate(path) - React Router
    ↓
Sidebar closes
    ↓
Page loads
```

---

## 📊 Menu Structure

```
┌─────────────────────────────────────┐
│  BQS Menu                      [X]  │
├─────────────────────────────────────┤
│  John Doe                           │
│  john@example.com                   │
│  PRACTICE_HEAD, SA                  │
├─────────────────────────────────────┤
│  PRACTICE HEAD                      │
│  📥 Unassigned Opportunities        │
│  ✓  Assign to SA                    │
│  📄 Review Assessments              │
│  📊 Practice Metrics                │
├─────────────────────────────────────┤
│  SOLUTION ARCHITECT                 │
│  📥 My Assigned Opportunities       │
│  📄 Start Assessment                │
│  ✓  Submitted Assessments           │
├─────────────────────────────────────┤
│  GENERAL                            │
│  ⚙️  Settings                        │
├─────────────────────────────────────┤
│  BQS v1.0 - Bid Qualification System│
└─────────────────────────────────────┘
```

---

## 🎨 Design Features

### **Sidebar Styling:**
- Width: 280px
- Background: White
- Shadow: Soft drop shadow
- Animation: Slide in from left (0.3s)

### **Sections:**
- Section headers: Uppercase, gray, 11px
- Menu items: 14px, with icons
- Hover: Yellow highlight (#FFF9C4)

### **User Info:**
- Name: Bold, 14px
- Email: Gray, 12px
- Roles: Blue, 11px

---

## 🚀 How to Use

### **1. Click Hamburger Menu**
Click the ☰ icon in the top-left corner

### **2. Sidebar Opens**
Shows menu items based on your role

### **3. Navigate**
Click any menu item to navigate to that page

### **4. Close**
- Click X button
- Click outside sidebar (on overlay)

---

## 📝 Role Combinations

Users can have multiple roles:

### **Example 1: Practice Head + SA**
```
Shows:
- Practice Head section (4 items)
- Solution Architect section (3 items)
- General section (1 item)
```

### **Example 2: Management Only**
```
Shows:
- Management section (4 items)
- General section (1 item)
```

### **Example 3: All Roles**
```
Shows:
- Management section (4 items)
- Practice Head section (4 items)
- Solution Architect section (3 items)
- General section (1 item)
```

---

## 🔧 Customization

### **Add New Menu Item:**

```typescript
<MenuItem
    icon={<YourIcon size={18} />}
    label="Your Label"
    onClick={() => handleNavigation('/your/path')}
/>
```

### **Add New Role Section:**

```typescript
{hasRole('YOUR_ROLE') && (
    <>
        <div style={{...}}>Your Role</div>
        <MenuItem ... />
    </>
)}
```

---

## ✅ Integration Checklist

- [x] ✅ RoleSidebar component created
- [x] ✅ Integrated with UserContext
- [x] ✅ Role-based menu items
- [x] ✅ Management section (4 items)
- [x] ✅ Practice Head section (4 items)
- [x] ✅ Solution Architect section (3 items)
- [x] ✅ General section (1 item)
- [x] ✅ Hamburger menu opens sidebar
- [x] ✅ Click outside closes sidebar
- [x] ✅ Smooth animations
- [x] ✅ Oracle-style design
- [x] ✅ User info display
- [x] ✅ Navigation integration

---

## 🎯 Next Steps

### **Create the Pages:**

You'll need to create these page components:

**Management:**
- `frontend/src/pages/ManagementDashboard.tsx`
- `frontend/src/pages/PortfolioAnalytics.tsx`
- `frontend/src/pages/FinalApprovals.tsx`
- `frontend/src/pages/TeamPerformance.tsx`

**Practice Head:**
- `frontend/src/pages/PracticeHeadUnassigned.tsx`
- `frontend/src/pages/AssignToSA.tsx`
- `frontend/src/pages/ReviewAssessments.tsx`
- `frontend/src/pages/PracticeMetrics.tsx`

**Solution Architect:**
- `frontend/src/pages/SAAssess.tsx`
- `frontend/src/pages/SASubmitted.tsx`

**General:**
- `frontend/src/pages/Settings.tsx`

### **Add Routes in App.tsx:**

```typescript
<Routes>
    {/* Management */}
    <Route path="/management/dashboard" element={<ManagementDashboard />} />
    <Route path="/management/analytics" element={<PortfolioAnalytics />} />
    <Route path="/management/approvals" element={<FinalApprovals />} />
    <Route path="/management/team" element={<TeamPerformance />} />
    
    {/* Practice Head */}
    <Route path="/practice-head/unassigned" element={<PracticeHeadUnassigned />} />
    <Route path="/practice-head/assign" element={<AssignToSA />} />
    <Route path="/practice-head/review" element={<ReviewAssessments />} />
    <Route path="/practice-head/metrics" element={<PracticeMetrics />} />
    
    {/* Solution Architect */}
    <Route path="/sa/assess" element={<SAAssess />} />
    <Route path="/sa/submitted" element={<SASubmitted />} />
    
    {/* General */}
    <Route path="/settings" element={<Settings />} />
</Routes>
```

---

## 📊 Summary

**Created:**
- ✅ Role-based sidebar menu
- ✅ 3 role sections (Management, Practice Head, SA)
- ✅ 11 total menu items
- ✅ User info display
- ✅ Smooth animations
- ✅ Oracle-style design

**Integrated with:**
- ✅ UserContext (existing)
- ✅ React Router (existing)
- ✅ OracleHeader (updated)

**Ready to:**
- ✅ Click hamburger menu
- ✅ See role-based options
- ✅ Navigate to pages

**Your role-based navigation is complete! Click the hamburger menu to see it in action!** 🎉
