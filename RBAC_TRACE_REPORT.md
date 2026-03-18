# 🛡️ RBAC Trace & Fix Report

## 🔍 Problem Identification
The Opportunity Scoring App was experiencing an RBAC mismatch where users identified as "Bid Manager" or "Sales Lead" were having their actions rejected by both the backend and frontend.

### Root Causes
1.  **Role Code Mismatch**: The backend and frontend code were hardcoded to check for `BID_MANAGER` and `SALES_LEAD` role codes. However, these specific codes were NOT present in the database seeding logic OR the `.env` configuration.
2.  **Missing Database Roles**: The seeded roles were `GH`, `PH`, `SH`, `SA`, `SP`. There were no roles for `BM` or `SL`.
3.  **Frontend Type Mismatch**: The `AuthContext.tsx` `UserRole` type did not include the expected roles, causing potential runtime issues even if the backend returned them.

## 🛠️ Implementation & Fixes

### 1. Database Alignment
- **New Role Codes**: Standardized on `BM` (Bid Manager) and `SL` (Sales Lead) to match the existing 2-letter convention (`GH`, `PH`, `SA`, etc.).
- **Updated `.env`**: Added `10:BM:Bid Manager` and `11:SL:Sales Lead` to the `INITIAL_ROLES` environment variable.
- **Seeding Script**: Executed [fix_rbac_roles.py](file:///c:/Users/YasasviUpadrasta/Documents/Data%20Analytics/Internal%20Innovation/BQS/tmp/fix_rbac_roles.py) to create these roles in the database and assign them to test users:
    - **John Doe (sa-001)**: Assigned `BM` role.
    - **Robert Chen (sh-001)**: Assigned `SL` role.

### 2. Backend Updates
- **Standardized Checks**: Replaced all occurrences of `BID_MANAGER` and `SALES_LEAD` with `BM` and `SL` across the following routers:
    - [opportunities.py](file:///c:/Users/YasasviUpadrasta/Documents/Data%20Analytics/Internal%20Innovation/BQS/backend/app/routers/opportunities.py)
    - [scoring.py](file:///c:/Users/YasasviUpadrasta/Documents/Data%20Analytics/Internal%20Innovation/BQS/backend/app/routers/scoring.py)
    - [upload.py](file:///c:/Users/YasasviUpadrasta/Documents/Data%20Analytics/Internal%20Innovation/BQS/backend/app/routers/upload.py)
- **Bug Fix**: Resolved a `NameError` in `scoring.py` where `user_role_codes` was being accessed before being defined in the `reopen_assessment` endpoint.

### 3. Frontend Updates
- **AuthContext.tsx**:
    - Updated `UserRole` type to include `'BM' | 'SL'`.
    - Updated `ROLE_LABELS` to map `BM` -> "Bid Manager" and `SL` -> "Sales Lead".
- **Component Logic**: Updated `isBM` and `isSL` checks in `ScoreOpportunity.tsx` and `OpportunityDetail.tsx` to use the new codes.
- **TopBar.tsx**: Added "Bid Manager" and "Sales Lead" to the quick role-switcher for easier testing and demonstration.

## ✅ Verification Steps
1.  **JWT Inspection**: Token payload now correctly includes `["BM"]` or `["SL"]` for the assigned users.
2.  **Frontend Display**: Users with the `BM` role now correctly display as "Bid Manager" in the TopBar.
3.  **Action Validation**: 
    - Bid Managers can now successfully save drafts, submit scores, and upload documents.
    - Sales Leads can now modify financial data in the Opportunity Detail page.
    - RBAC rejection (403) correctly occurs for unauthorized roles (e.g., `SA`, `SP`).

---
*Report Generated: March 13, 2026*
