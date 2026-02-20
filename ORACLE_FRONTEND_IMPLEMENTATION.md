# 🎨 Oracle Inspira Frontend Implementation

## Overview
Created a frontend that matches the Oracle Inspira CRM interface with the cream/yellow color scheme and professional table layout.

---

## 📋 What Was Created

### **1. CSS Theme (`frontend/src/index.css`)**
**Oracle Inspira Color Palette:**
- Cream background: `#F5F1E3`
- Yellow accents: `#FFE082`
- Red badges: `#C62828`
- Green win badges: `#2E7D32`

**Features:**
- ✅ Oracle-style header with cream background
- ✅ Professional table styling
- ✅ Win probability badges (green/yellow/red)
- ✅ Status badges
- ✅ Hover effects
- ✅ Responsive design

---

### **2. Oracle Header Component (`frontend/src/components/OracleHeader.tsx`)**

**Features:**
- ✅ Cream background (#F5F1E3)
- ✅ "inspira" logo with "Great Place To Work" badge
- ✅ Icon buttons: Search, Notifications (with badge), Favorites, Messages, Profile
- ✅ Hamburger menu

**Matches Screenshot:**
```
[☰] inspira [GPTW Badge]                    [🔍] [🔔¹] [⭐] [💬] [👤]
```

---

### **3. Opportunities Table (`frontend/src/pages/OpportunityInbox.tsx`)**

**Features:**
- ✅ Page title with help icon
- ✅ Search toolbar (Find by Name)
- ✅ List filter dropdown (All Opportunities)
- ✅ Actions button
- ✅ Create Opportunity button (blue)
- ✅ View selector
- ✅ Data table with columns:
  - Win (%) - Green/yellow/red badges
  - Opportunity Nbr
  - Name (clickable link)
  - Owner
  - Practice
  - Status (badge)
  - Creation Date
  - Account
  - Account Owner
  - Amount (right-aligned, formatted)
  - Estimated Billing
  - Sales Stage
  - Region

**Table Styling:**
- ✅ Gray header row
- ✅ Hover effect (yellow highlight)
- ✅ Clickable rows
- ✅ Professional borders
- ✅ Proper spacing

---

### **4. Layout Component (`frontend/src/components/Layout.tsx`)**
Simple wrapper with white background.

---

## 🎨 Design Features

### **Color Scheme:**
```css
Cream Header:     #F5F1E3
Yellow Hover:     #FFF9C4
Red Badges:       #C62828
Green Win High:   #2E7D32
Blue Links:       #1976D2
Gray Text:        #757575
```

### **Typography:**
- Font: System fonts (Segoe UI, Roboto, etc.)
- Sizes: 12px (table), 14px (body), 20px (titles)
- Weights: 400 (normal), 600 (headers)

### **Components:**
1. **Win Probability Badges:**
   - High (≥70%): Green background, white text
   - Medium (40-69%): Yellow background, dark text
   - Low (<40%): Red background, white text

2. **Status Badges:**
   - Committed: Green tint
   - Forecast: Orange tint

3. **Buttons:**
   - Default: White with border
   - Primary: Blue background
   - Hover: Yellow tint

---

## 🚀 How to Use

### **1. Install Dependencies**
```bash
cd frontend
npm install lucide-react
```

### **2. Start Frontend**
```bash
npm run dev
```

### **3. Start Backend**
```bash
cd ..
python -m backend.app.main
```

### **4. Open Browser**
```
http://localhost:5173
```

---

## 📊 Features Implemented

### **Header:**
- [x] Cream background
- [x] inspira logo
- [x] Great Place To Work badge
- [x] Search icon
- [x] Notifications with badge
- [x] Favorites icon
- [x] Messages icon
- [x] Profile icon

### **Toolbar:**
- [x] Find search box
- [x] List dropdown filter
- [x] View options button
- [x] Actions dropdown
- [x] Create Opportunity button

### **Table:**
- [x] Win % column with colored badges
- [x] Opportunity Number
- [x] Name (clickable link)
- [x] Owner
- [x] Practice
- [x] Status badge
- [x] Creation Date (formatted)
- [x] Account
- [x] Account Owner
- [x] Amount (currency formatted)
- [x] Estimated Billing
- [x] Sales Stage
- [x] Region

### **Interactions:**
- [x] Search functionality
- [x] Filter dropdown
- [x] Row hover effect
- [x] Clickable rows (navigate to detail)
- [x] Clickable opportunity names

---

## 🎯 Matching the Screenshot

### **Header:**
✅ Cream background (#F5F1E3)
✅ inspira logo with GPTW badge
✅ Icon buttons on right

### **Page Title:**
✅ "Opportunities" with help icon
✅ White background
✅ Bottom border

### **Toolbar:**
✅ Find search with label
✅ List dropdown
✅ Actions button
✅ Create Opportunity (blue)

### **Table:**
✅ Gray header row
✅ Win % badges (green 100)
✅ Clickable blue links
✅ Status badges
✅ Formatted dates
✅ Currency amounts
✅ Yellow hover effect

---

## 📱 Responsive Design

The table is scrollable horizontally on smaller screens while maintaining the Oracle look and feel.

---

## 🔧 Customization

### **Change Colors:**
Edit `frontend/src/index.css`:
```css
:root {
  --oracle-cream: #F5F1E3;  /* Header background */
  --oracle-yellow: #FFE082; /* Accents */
  --oracle-red: #C62828;    /* Badges */
  /* ... */
}
```

### **Add More Columns:**
Edit `frontend/src/pages/OpportunityInbox.tsx`:
```tsx
<th>New Column</th>
// ...
<td>{opp.new_field}</td>
```

### **Change Logo:**
Edit `frontend/src/components/OracleHeader.tsx`:
```tsx
<div className="oracle-logo">
    Your Logo Here
</div>
```

---

## 📊 Data Flow

```
Backend API (localhost:8000)
    ↓
GET /api/inbox/unassigned
    ↓
OpportunityInbox.tsx (fetch)
    ↓
Display in Oracle-style table
    ↓
User clicks row
    ↓
Navigate to /score/:id
```

---

## ✅ Checklist

- [x] Oracle cream header
- [x] inspira logo with badge
- [x] Icon buttons
- [x] Search toolbar
- [x] Filter dropdown
- [x] Actions button
- [x] Create button (blue)
- [x] Data table
- [x] Win % badges
- [x] Status badges
- [x] Clickable links
- [x] Hover effects
- [x] Currency formatting
- [x] Date formatting
- [x] Responsive design

---

## 🎉 Result

Your frontend now looks like Oracle Inspira CRM with:
- ✅ Cream/yellow color scheme
- ✅ Professional table layout
- ✅ Win probability badges
- ✅ Status indicators
- ✅ Proper typography
- ✅ Hover interactions
- ✅ Responsive design

**Start the frontend with `npm run dev` and see the Oracle-style interface!** 🚀
