/**
 * API Endpoints
 * These mirror the routing structure of the FastAPI backend.
 */
export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/api/auth/sso-login',
        ME: '/api/auth/me',
        USERS: '/api/auth/users',
    },
    OPPORTUNITIES: {
        BASE: '/api/opportunities',
        BY_ID: (id: string) => `/api/opportunities/${id}`,
        APPROVE: (id: string) => `/api/opportunities/${id}/approve`,
        ASSIGN: (id: string) => `/api/opportunities/${id}/assign`,
        START_ASSESSMENT: (id: string) => `/api/opportunities/${id}/start-assessment`,
        METADATA: {
            REGIONS: '/api/opportunities/metadata/regions',
            PRACTICES: '/api/opportunities/metadata/practices',
            STAGES: '/api/opportunities/metadata/stages',
            STATUSES: '/api/opportunities/metadata/statuses',
        },
        DOCUMENT_CATEGORIES: '/api/opportunities/document-categories',
    },
    INBOX: {
        BASE: '/api/inbox',
        BY_ID: (id: string) => `/api/inbox/${id}`,
        UNASSIGNED: '/api/inbox/unassigned',
        MY_ASSIGNMENTS: '/api/inbox/my-assignments',
        ASSIGN: '/api/inbox/assign',
    },
    SCORING: {
        BASE: '/api/scoring',
        CONFIG: '/api/scoring/config',
        LATEST: (id: string) => `/api/scoring/${id}/latest`,
        HISTORY: (id: string) => `/api/scoring/${id}/history`,
        DRAFT: (id: string) => `/api/scoring/${id}/draft`,
        SUBMIT: (id: string) => `/api/scoring/${id}/submit`,
        COMBINED_REVIEW: (id: string) => `/api/scoring/${id}/combined-review`,
        NEW_VERSION: (id: string) => `/api/scoring/${id}/new-version`,
        REOPEN: (id: string) => `/api/scoring/${id}/reopen`,
    },
    UPLOAD: '/api/upload',
    SYNC: {
        DATABASE: '/api/sync-database',
        FORCE: '/api/sync-force',
    },
    BATCH_SYNC: {
        START: '/api/batch-sync/start',
        STATUS: '/api/batch-sync/status',
        RESET: '/api/batch-sync/reset',
    }
};
