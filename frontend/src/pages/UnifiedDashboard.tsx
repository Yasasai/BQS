import React, { useState, useEffect, useMemo } from 'react';
import { useAuth, UserRole } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';

/**
 * UnifiedDashboard
 * A single, consolidated workspace for all user roles (GH, PH, SH, SA, SP).
 * Handles dynamic data fetching, metrics, and role-based filtering.
 */
export const UnifiedDashboard: React.FC = () => {
    const { user, token } = useAuth();
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<any[]>([]);
    const [counts, setCounts] = useState<any>({});
    const [metrics, setMetrics] = useState({ total_value: 0, total_count: 0 });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('ALL');
    const [searchQuery, setSearchQuery] = useState('');

    // Fetch data from the consolidated Opportunities API
    const fetchDashboardData = async () => {
        if (!user) return;

        setIsLoading(true);
        setError(null);

        try {
            // Note: Our backend router already handles role filtering via access logic,
            // but we pass common parameters to ensure the results are tuned for the user.
            const response = await apiClient.get(API_ENDPOINTS.OPPORTUNITIES.BASE, {
                params: {
                    user_id: user.id,
                    role: user.role,
                    tab: activeTab === 'ALL' ? null : activeTab.toLowerCase(),
                    search: searchQuery || null
                }
            });

            setOpportunities(response.data.items || []);
            setCounts(response.data.counts || {});
            setMetrics({
                total_value: response.data.total_value || 0,
                total_count: response.data.total_count || 0
            });
        } catch (err: any) {
            console.error("❌ Failed to fetch dashboard data:", err);
            setError(err?.response?.data?.detail || "Could not load opportunities. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
    }, [user, activeTab]);

    // Role detection
    const isExecutive = user?.role === 'GH' || (user?.role as any) === 'PSH';
    const isApprovalRole = user?.role === 'PH' || user?.role === 'SH';

    // UI Configuration based on role
    const dashboardTitle = useMemo(() => {
        if (isExecutive) return "Global Pipeline Overview";
        if (isApprovalRole) return `${user?.displayRole} Workspace`;
        return "Opportunity Assignment Inbox";
    }, [user]);

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(val);
    };

    return (
        <div style={{
            padding: '40px',
            minHeight: '100vh',
            background: '#f8fafc',
            fontFamily: "'Outfit', 'Inter', sans-serif"
        }}>
            {/* Header Section */}
            <header style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '32px'
            }}>
                <div>
                    <div style={{
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#6366f1',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        marginBottom: '4px'
                    }}>
                        Console / Workspace
                    </div>
                    <h1 style={{
                        fontSize: '28px',
                        fontWeight: 800,
                        color: '#1e293b',
                        margin: 0,
                        letterSpacing: '-0.02em'
                    }}>
                        {dashboardTitle}
                    </h1>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        background: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        padding: '2px 16px',
                        boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                    }}>
                        <span style={{ marginRight: '8px', opacity: 0.4 }}>🔍</span>
                        <input
                            type="text"
                            placeholder="Search opportunities..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && fetchDashboardData()}
                            style={{
                                border: 'none',
                                outline: 'none',
                                padding: '10px 0',
                                fontSize: '14px',
                                width: '240px'
                            }}
                        />
                    </div>
                    <button
                        onClick={fetchDashboardData}
                        style={{
                            padding: '10px 18px',
                            background: '#fff',
                            border: '1px solid #e2e8f0',
                            borderRadius: '12px',
                            fontWeight: 600,
                            color: '#475569',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'all 0.2s ease',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#f1f5f9'}
                        onMouseLeave={(e) => e.currentTarget.style.background = '#fff'}
                    >
                        <span>🔄</span> {isLoading ? 'Syncing...' : 'Refresh'}
                    </button>
                </div>
            </header>

            {/* Metrics Grid (Global/High level) */}
            {(isExecutive || isApprovalRole) && (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '24px',
                    marginBottom: '40px'
                }}>
                    {[
                        { label: 'Pipeline Total', value: formatCurrency(metrics.total_value), sub: `${metrics.total_count} deals in flight`, icon: '💰', color: '#6366f1' },
                        { label: 'Draft / Scoring', value: counts?.DRAFT || 0, sub: 'Needs technical review', icon: '📝', color: '#f59e0b' },
                        { label: 'Awaiting Approval', value: counts?.PENDING_APPROVAL || 0, sub: 'Action required by LEADS', icon: '⚡', color: '#ef4444' },
                        { label: 'Completed', value: counts?.SUBMIT_WON || counts?.COMPLETED || 0, sub: 'Successfully processed', icon: '✅', color: '#10b981' },
                    ].map((m, idx) => (
                        <div key={idx} style={{
                            background: '#fff',
                            padding: '24px',
                            borderRadius: '20px',
                            border: '1px solid #edf2f7',
                            boxShadow: '0 4px 12px -2px rgba(0,0,0,0.03)',
                            position: 'relative',
                            overflow: 'hidden'
                        }}>
                            <div style={{ position: 'absolute', top: 0, left: 0, height: '4px', width: '100%', background: m.color }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                                <div style={{ fontSize: '13px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>{m.label}</div>
                                <div style={{ fontSize: '20px' }}>{m.icon}</div>
                            </div>
                            <div style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', marginBottom: '4px' }}>{m.value}</div>
                            <div style={{ fontSize: '12px', color: '#94a3b8' }}>{m.sub}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* Main Table View */}
            <div style={{
                background: '#fff',
                borderRadius: '20px',
                border: '1px solid #edf2f7',
                boxShadow: '0 4px 20px -2px rgba(0,0,0,0.05)',
                overflow: 'hidden'
            }}>
                {/* Tabs */}
                <div style={{
                    display: 'flex',
                    borderBottom: '1px solid #f1f5f9',
                    padding: '0 24px'
                }}>
                    {['ALL', 'PENDING_APPROVAL', 'MY_ASSIGNMENTS', 'COMPLETED'].map((tab) => {
                        const label = tab.replace('_', ' ');
                        const isActive = activeTab === tab;
                        return (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                style={{
                                    padding: '20px 16px',
                                    background: 'none',
                                    border: 'none',
                                    borderBottom: isActive ? '3px solid #6366f1' : '3px solid transparent',
                                    color: isActive ? '#1e293b' : '#94a3b8',
                                    fontWeight: isActive ? 700 : 500,
                                    fontSize: '14px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    marginRight: '20px'
                                }}
                            >
                                {label}
                            </button>
                        );
                    })}
                </div>

                {/* Table */}
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead>
                            <tr style={{ background: '#f8fafc', borderBottom: '1px solid #f1f5f9' }}>
                                <th style={thStyle}>Opportunity</th>
                                <th style={thStyle}>Details & Value</th>
                                <th style={thStyle}>Score</th>
                                <th style={thStyle}>Status</th>
                                <th style={thStyle}>Assignees</th>
                                <th style={thStyle}>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={5} style={{ padding: '80px', textAlign: 'center' }}>
                                        <div style={{ display: 'inline-block', width: '32px', height: '32px', border: '3px solid #e2e8f0', borderTopColor: '#6366f1', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                                        <div style={{ marginTop: '16px', color: '#64748b', fontSize: '14px' }}>Fetching latest data...</div>
                                    </td>
                                </tr>
                            ) : opportunities.length === 0 ? (
                                <tr>
                                    <td colSpan={5} style={{ padding: '80px', textAlign: 'center' }}>
                                        <div style={{ fontSize: '40px', marginBottom: '16px' }}>📂</div>
                                        <div style={{ fontSize: '18px', fontWeight: 600, color: '#334155' }}>No records found</div>
                                        <div style={{ color: '#94a3b8', fontSize: '14px' }}>Try changing your filters or searching for something else.</div>
                                    </td>
                                </tr>
                            ) : (
                                opportunities.map((opp) => (
                                    <tr key={opp.id} style={{
                                        borderBottom: '1px solid #f1f5f9',
                                        transition: 'background 0.2s ease',
                                    }} onMouseEnter={(e) => e.currentTarget.style.background = '#fbfcfd'} onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '2px', cursor: 'pointer' }} onClick={() => navigate(`/opportunity/${opp.id}`)}>
                                                {opp.name}
                                            </div>
                                            <div style={{ fontSize: '11px', color: '#94a3b8', fontFamily: 'monospace' }}>#{opp.remote_id || 'LOCAL-ID'} • {opp.customer}</div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ fontWeight: 600, color: '#0f172a' }}>{formatCurrency(opp.deal_value)}</div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>{opp.practice} • {opp.geo}</div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{
                                                fontSize: '14px',
                                                fontWeight: 800,
                                                color: (opp.overall_score || 0) >= 4 ? '#166534' : (opp.overall_score || 0) >= 3 ? '#1e40af' : '#1e293b'
                                            }}>
                                                {opp.overall_score || opp.win_probability || '-'}
                                            </div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{
                                                display: 'inline-flex',
                                                padding: '4px 10px',
                                                borderRadius: '99px',
                                                fontSize: '11px',
                                                fontWeight: 800,
                                                letterSpacing: '0.05em',
                                                ...getStatusStyle(opp.workflow_status)
                                            }}>
                                                {opp.workflow_status?.replace('_', ' ')}
                                            </div>
                                        </td>
                                        <td style={tdStyle}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                {opp.assigned_sa && <span style={roleBadgeStyle}>🔧 {opp.assigned_sa}</span>}
                                                {opp.assigned_practice_head && <span style={roleBadgeStyle}>🏛️ {opp.assigned_practice_head}</span>}
                                                {opp.assigned_legal && <span style={roleBadgeStyle}>⚖️ {opp.assigned_legal}</span>}
                                                {opp.assigned_finance && <span style={roleBadgeStyle}>💰 {opp.assigned_finance}</span>}
                                                {!opp.assigned_sa && !opp.assigned_practice_head && !opp.assigned_legal && !opp.assigned_finance && <span style={{ color: '#cbd5e1', fontSize: '12px' }}>Unassigned</span>}
                                            </div>
                                        </td>
                                        <td style={tdStyle}>
                                            <button
                                                onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                style={{
                                                    padding: '8px 16px',
                                                    background: '#6366f1',
                                                    color: '#fff',
                                                    border: 'none',
                                                    borderRadius: '8px',
                                                    fontSize: '13px',
                                                    fontWeight: 600,
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
            `}</style>
        </div>
    );
};

const thStyle: React.CSSProperties = {
    padding: '16px 24px',
    fontSize: '12px',
    fontWeight: 700,
    color: '#64748b',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
};

const tdStyle: React.CSSProperties = {
    padding: '20px 24px',
    fontSize: '14px',
    verticalAlign: 'middle'
};

const roleBadgeStyle: React.CSSProperties = {
    fontSize: '11px',
    color: '#475569',
    background: '#f1f5f9',
    padding: '2px 8px',
    borderRadius: '4px',
    width: 'fit-content'
};

const getStatusStyle = (status: string) => {
    switch (status) {
        case 'SUBMIT_WON': case 'COMPLETED': return { background: '#dcfce7', color: '#166534' };
        case 'PENDING_APPROVAL': return { background: '#fee2e2', color: '#991b1b', border: '1px solid rgba(153,27,27,0.1)' };
        case 'UNDER_ASSESSMENT': return { background: '#e0e7ff', color: '#3730a3' };
        case 'DRAFT': return { background: '#fef3c7', color: '#92400e' };
        default: return { background: '#f1f5f9', color: '#475569' };
    }
};

export default UnifiedDashboard;
