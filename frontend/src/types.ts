export interface Opportunity {
    id: number;
    remote_id: string; // Oracle Opportunity Number
    name: string;      // Oracle Name
    customer: string;  // Oracle Account
    practice: string;  // Oracle Practice
    geo: string;
    region?: string;   // Oracle Region
    sector?: string;   // Oracle Sector
    deal_value: number;
    currency: string;
    win_probability?: number; // Oracle Win (%)
    sales_owner: string;      // Oracle Owner
    stage: string;            // Oracle Sales Stage
    close_date: string;
    expected_po_date?: string; // Expected PO Date
    estimated_billing_date?: string; // Oracle Estimated Billing Date
    rfp_date?: string;
    remote_url?: string;
    last_synced_at: string;

    // 3-Role Workflow Status
    status?: string; // Internal Status for workflow (New, Scoring Pending, etc.)
    workflow_status?: string;

    // Assignment IDs
    assigned_practice_head_id?: string;
    assigned_sales_head_id?: string;
    assigned_sa_id?: string;
    assigned_sp_id?: string;

    assigned_practice_head?: string; // Display Name
    assigned_sa?: string;      // Display Name
    assigned_sp?: string;      // Display Name
    assigned_sales_head?: string; // Display Name

    // Approval Statuses
    gh_approval_status?: 'PENDING' | 'APPROVED' | 'REJECTED';
    ph_approval_status?: 'PENDING' | 'APPROVED' | 'REJECTED';
    sh_approval_status?: 'PENDING' | 'APPROVED' | 'REJECTED';
    combined_submission_ready?: boolean;

    // Timestamps
    assigned_to_practice_at?: string;
    assigned_to_sa_at?: string;
    submitted_for_review_at?: string;
    approved_by_practice_at?: string;
    final_decision_at?: string;

    // Decisions
    practice_head_decision?: string;
    practice_head_comments?: string;
    management_decision?: string;
    management_comments?: string;

    // UI specific
    current_stage?: string;
    governance_status?: string;
    pending_with?: string;
    stage_entered_at?: string;

    // Lock
    locked_by?: string;
    locked_at?: string;
}

export interface Assessment {
    id: number;
    opp_id: number;
    version: string;
    scores: Record<string, number>;
    comments: string;
    is_submitted: boolean;
    created_at: string;
    created_by: string;
}
