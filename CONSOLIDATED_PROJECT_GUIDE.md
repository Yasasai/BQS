# 📘 BQS: Consolidated Project Guide (Pin-to-Pin)

This document provides an exhaustive overview of the **Bid Qualification System (BQS)**, covering everything from initial infrastructure to complex business logic added during development.

---

## 🚀 1. Project Identity & Mission
**BQS** is a data-driven decision platform designed to transform "gut-feeling" sales into strategic organizational choices. It synchronizes opportunities from **Oracle CRM** and subjects them to a rigorous **9-point qualification framework**.

- **Goal**: Standardize opportunity assessment and ensure organizational alignment.
- **Outcome**: Data-driven GO/NO-GO decisions with executive transparency.

---

## 🛠️ 2. Comprehensive Tech Stack

### Backend (The Engine)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) for high-performance asynchronous API endpoints.
- **Server**: [Uvicorn](https://www.uvicorn.org/) as the ASGI server for local development and production.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) with [PostgreSQL](https://www.postgresql.org/) for robust, relational data management.
- **Authentication**: JWT-based security with **Azure AD SSO** integration and a Developer Bypass (Dev Login).
- **Automation**: `APScheduler` for daily midnight CRM syncs.
- **Extraction**: `httpx` for parallel REST API fetches; `Selenium` as a fallback UI scraper.

### Frontend (The Interface)
- **Library**: [React 18](https://reactjs.org/) (Functional Components with Hooks).
- **Build Tool**: [Vite](https://vitejs.dev/) for lightning-fast HMR and bundling.
- **Language**: [TypeScript](https://www.typescriptlang.org/) for type-safe state management.
- **Icons**: [Lucide React](https://lucide.dev/) for modern visual cues.
- **State Management**: React Context API (`AuthContext`, `UserContext`) for hierarchical permissions.

---

## 🗄️ 3. Database Architecture (Exhaustive Schema)

The PostgreSQL schema is the core source of truth for the BQS workflow.

### Reference & Security
- **`app_user`**: Stores name, email, geo-region, and the critical `manager_email` for hierarchy filtering.
- **`role` & `user_role`**: Maps users to permissions (GH, PH, SH, SA, SP, LEGAL, FINANCE, BM).

### Workflow & Opportunities
- **`opportunity`**: The central table tracking `workflow_status`, `pat_margin`, and assignments (`assigned_sa_ids`, `assigned_practice_head_ids`, etc.).
- **`practice`**: Reference data for technological business units.

### Assessment & Scoring
- **`opp_score_version`**: Tracks multiple assessments for a single opportunity.
- **`opp_score_values`**: Stores granular 0.5-increment scores (0-5) for each of the 9 sections.
- **`opp_score_section`**: Defines the "Single Source of Truth" for section weights and reasoning.

### Ingestion & Sync
- **`sync_run` & `sync_logs`**: Audit trail for CRM synchronization.
- **`crm_sync_watermark`**: Tracks offsets for the resumable batch sync system.
- **`oracle_opportunities_offset`**: Staging table for resumable ID extraction.

---

## 🔄 4. Data Ingestion Mechanisms

### A. Parallel Incremental Sync (`oracle_sync.py`)
- **Logic**: Uses `LastUpdateDate` to fetch only changed records.
- **Performance**: 5 concurrent workers fetching 50 records each (250 items/batch).
- **Safety**: 90-second timeout with auto-retry.

### B. Resumable Batch Sync (`batch_sync_with_offset.py`)
- **Logic**: Uses Oracle `MyOpportunitiesFinder` with `RecordSet='ALLOPTIES'`.
- **Feature**: Resumes from the last known `current_offset` if interrupted.
- **Purpose**: Massive initial loads of 1000+ records in chunks of 5-10.

---

## ⚖️ 5. Scoring & Business Logic (The "Brain")

### The 9-Point Framework
BQS evaluates deals on scales of 0-5 across:
1. **Strategic Fit**
2. **Win Probability**
3. **Competitive Position**
4. **Financial Value**
5. **Delivery Feasibility**
6. **Customer Relationship**
7. **Risk Exposure**
8. **Product Compliance**
9. **Legal Readiness**

### Calculation Math
- **Weighted Overall Score**: `(sum(score * weight) / (sum(weight) * 5)) * 100`
- **Result**: A 0-100 percentage score representing deal quality.

### Compliance Routing (The 5Cr/5% Rule)
- **Trigger**: `Deal Value > 50,000,000` AND `PAT Margin < 5%`.
- **Outcome**: Automatically flags **Mandatory Review** from Legal and Finance roles.

---

## 🔒 6. RBAC & Hierarchical Visibility

### Role Hierarchy Mapping
- **Geo Head (GH)**: Global visibility; Administrative user management.
- **Practice/Sales Head (PH/SH)**: View their own assigned deals + any deal where the owner reports to them (`manager_email`).
- **Solution Architect (SA) / Salesperson (SP)**: Restricted to their specific assignments.
- **Bid Manager (BM)**: Orchestrator with exclusive rights to modify/submit scores.

### Front-to-Back Enforcement
- **Backend**: `OpportunityService` injects SQL `WHERE` clauses based on `user_id` and `role`.
- **Frontend**: Role-based routing in `App.tsx` and conditional UI rendering.

---

## 🛠️ 7. Maintenance & Troubleshooting

### Self-Healing Logic
- **Database**: `heal_database.py` automatically adds missing columns to survive schema updates.
- **Assignments**: Auto-creates users in the DB if an assignment is made to an un-provisioned email.

### Essential Scripts
- `clean_restart.py`: Flushes cache and forces a full CRM re-sync.
- `diag_env.py`: Validates `.env` variables and DB connectivity.
- `batch_sync_with_offset.py status`: Checks the health of the background ingestion engine.

---
*Created for Yasasvi / Inspira BQS Internal Innovation.*
