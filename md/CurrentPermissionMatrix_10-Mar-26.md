### Role: GH - Global Head
* **Accessible UI Routes**: `/management/*` (with fallback access to `/practice-head/*`, `/sales/*`, `/assigned-to-me`, and `/sa/*`). Redirects to `/management/dashboard`.
* **Sidebar Menu Items**: Home, Management Dashboard, Data Freshness & Sync (Sync Now Button).
* **Allowed Backend Actions**: Can call `POST /api/opportunities/{opp_id}/approve`, `POST /api/scoring/{opp_id}/review/approve`, and `POST /api/scoring/{opp_id}/review/reject`. Can trigger manual data syncs. Can also access any endpoint without assignment restrictions natively handled by services.
* **Data Visibility Filters**: Full pipeline oversight (bypasses user ID assignment filters to see all regional and practice data).

### Role: PH - Practice Head
* **Accessible UI Routes**: `/practice-head/*`. Redirects to `/practice-head/dashboard`.
* **Sidebar Menu Items**: Home, Practice Head Dashboard.
* **Allowed Backend Actions**: Can call `POST /api/opportunities/{opp_id}/approve`, `POST /api/scoring/{opp_id}/review/approve`, and `POST /api/scoring/{opp_id}/review/reject`.
* **Data Visibility Filters**: Practice review & approvals (can only see opportunities assigned to their `assigned_practice_head_id`).

### Role: SH - Sales Head
* **Accessible UI Routes**: `/sales/*` (including `/sales/dashboard`, `/sales/all`, and `/sales/action-required`). Redirects to `/sales/dashboard`.
* **Sidebar Menu Items**: Home, Dashboard, Action Required.
* **Allowed Backend Actions**: Can call `POST /api/opportunities/{opp_id}/approve`, `POST /api/scoring/{opp_id}/review/approve`, and `POST /api/scoring/{opp_id}/review/reject`.
* **Data Visibility Filters**: Sales pipeline management (can only see opportunities assigned to their `assigned_sales_head_id`).

### Role: SA - Solution Architect
* **Accessible UI Routes**: `/assigned-to-me`, `/sa/*`. Redirects to `/assigned-to-me`.
* **Sidebar Menu Items**: Home, My Tasks.
* **Allowed Backend Actions**: Can start assessments (`POST /api/opportunities/{opp_id}/start-assessment`), save drafts (`POST /api/scoring/{opp_id}/draft`), and submit assessments (`POST /api/scoring/{opp_id}/submit`).
* **Data Visibility Filters**: Opportunity scoring & assessment (can only see opportunities where `assigned_sa_id` matches their ID).

### Role: SP - Sales Person
* **Accessible UI Routes**: `/assigned-to-me`, `/sa/*`. Redirects to `/assigned-to-me`.
* **Sidebar Menu Items**: Home, My Tasks.
* **Allowed Backend Actions**: Can start assessments (`POST /api/opportunities/{opp_id}/start-assessment`), save drafts (`POST /api/scoring/{opp_id}/draft`), and submit assessments (`POST /api/scoring/{opp_id}/submit`).
* **Data Visibility Filters**: Opportunity submission (can only see opportunities where `assigned_sp_id` matches their ID).
