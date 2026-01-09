export interface Opportunity {
    id: number;
    remote_id: string;
    name: string;
    customer: string;
    practice: string;
    geo: string;
    deal_value: number;
    currency: string;
    win_probability?: number;
    sales_owner: string;
    stage: string;
    close_date: string;
    rfp_date?: string;
    last_synced_at: string;

    // 3-Role Workflow Status Machine
    workflow_status?: string;
    assigned_practice?: string;
    assigned_practice_head?: string;
    assigned_sa?: string;
    assigned_sa_secondary?: string;

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
