# BQS (Bid Qualification System) - Comprehensive Requirement & Functional Document

## 1. Executive Summary
The **Bid Qualification System (BQS)** is a strategic internal tool designed to streamline, standardize, and govern the "Go/No-Go" decision process for sales opportunities. It acts as a bridge between the **Oracle CRM Cloud** (Source of Truth) and a custom assessment framework, ensuring that every opportunity is evaluated by the right experts across multiple dimensions (Strategic Fit, Delivery, Finance, Risk) before pursuit.

---

## 2. Core Vision & Problem Statement
*   **Problem**: Opportunities in CRM lack a standardized qualification process. Assessments are often manual, scattered in emails/spreadsheets, and lack executive visibility.
*   **Solution**: A centralized platform that auto-syncs CRM data, enforces a multi-role review workflow, and generates a data-driven "BQS Score" for final management approval.

---

## 3. End-to-End Functional Architecture

### 🛡️ 3.1 Data Synchronization (The Foundation)
*   **Source**: Oracle CRM Cloud (REST API).
*   **Mechanism**: 
    *   **Dynamic Sync**: Automated daily cron jobs and manual "Force Sync" triggers.
    *   **Batch & Offset Tracking**: Implemented a robust, resumable sync logic that fetches data in batches (e.g., 50 records) using offsets to prevent memory overload and handle large volumes.
    *   **Self-Healing Schema**: The backend detects missing columns or tables on startup and automatically "heals" the database schema to match the latest code requirements.

### 👥 3.2 Role-Based Workflow (The Engine)
The system enforces a strict 4-tier hierarchy for every opportunity:

1.  **Management (GH/SH)**: 
    *   **Initial Gate**: Reviews new syncs from Oracle. Decides if an opportunity is even worth "BQS-ing."
    *   **Final Decision**: Approves or Rejects the deal based on the completed BQS score and Practice Head recommendation.
2.  **Practice Head (PH)**: 
    *   **Resource Allocation**: Assigns the opportunity to a specific Solution Architect (SA).
    *   **Quality Control**: Reviews the SA's assessment, adds practice-level risks, and gives a "Professional Opinion."
3.  **Solution Architect (SA)**:
    *   **Deep Dive**: The core assessor. Fills out the 9-factor scoring framework.
    *   **Evidence**: Uploads supporting documents and provides justifications for scores.
4.  **Sales Person (SP)**:
    *   **Collaborative Input**: Provides secondary scoring and commentary to ensure the "Sales view" is captured alongside the technical view.

### 📝 3.3 The 9-Factor BQS Framework
Opportunities are scored (0.5 to 5.0) across nine weighted dimensions:
1.  **Strategic Fit (15%)**: Alignment with company goals.
2.  **Win Probability (15%)**: Competitive landscape and relationship.
3.  **Financial Value (15%)**: Margins, payment terms, and size.
4.  **Competitive Position (10%)**: USP vs. Competitors.
5.  **Delivery Feasibility (10%)**: Technical capability and resource availability.
6.  **Customer Relationship (10%)**: Past history and credibility.
7.  **Risk Exposure (10%)**: Legal, technical, and commercial risks.
8.  **Product Compliance (5%)**: Standard vs. Custom requirements.
9.  **Readiness (10%)**: RFP clarity and timeline.

---

## 4. Key Performance & Resilience Features

### 🚀 4.1 "Nuclear" & "Batch" Sync Logic
*   **Async Gathering**: the system uses Python `asyncio` and `httpx` to fetch multiple pages of CRM data in parallel, significantly reducing sync time from minutes to seconds.
*   **Conflict Resolution**: If CRM data changes while an assessment is in progress, the system updates the metadata but **preserves** the internal BQS workflow status.

### 🎨 4.2 Premium User Experience
*   **Oracle-Fluent Design**: The UI mimics the look and feel of Oracle Cloud (Redwood design language) to reduce the learning curve for sales teams.
*   **Real-time Analytics**: Management sees a "Pipeline Health" dashboard with live metrics: Win Rate, Action Required counts, and total Pipeline Value.

### 🐳 4.3 Containerization (Docker)
*   The entire app is now "Dockerized."
*   **Inter-related Services**: Database (Postgres), Backend (FastAPI), and Frontend (React/Nginx) are wired together.
*   **Infrastructure-as-Code**: Deployment is reduced to a single command: `docker-compose up --build`.

---

## 5. How to Explain This to Stakeholders

### **For Executives (The Why)**:
> "BQS is our **Digital Governance Gate**. It ensures we don't waste time on low-margin or high-risk deals. It gives you a single dashboard to see every major deal in the company, its risk score, and who is working on it."

### **For Sales Leads (The How)**:
> "Your opportunities from Oracle show up here automatically. You assign an architect, they score the technicals, you add the sales perspective, and then leadership gives the final 'Go'. No more hunting for approvals in email."

### **For IT/Technical Teams (The What)**:
> "It's a modern React/FastAPI stack. It features a self-healing PostgreSQL DB and a parallelized sync engine for Oracle CRM. We've optimized it for performance using async processing and Docker for one-click deployment."

---

## 6. Development Milestones (Recap)
*   ✅ **Phase 1**: Core Sync (Oracle to Postgres).
*   ✅ **Phase 2**: Role Switcher & 9-Factor Framework UI.
*   ✅ **Phase 3**: Multi-Role Approval Workflow (SA → PH → GH).
*   ✅ **Phase 4**: Advanced Analytics & Portfolio Filtering.
*   ✅ **Phase 5**: Batch Sync Optimization & Offset Tracking.
*   ✅ **Phase 6**: Full Dockerization & Deployment Readiness.

---
*Created by Antigravity - Documenting the evolution of BQS*
