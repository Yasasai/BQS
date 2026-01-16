import React, { useState, useEffect } from 'react';
import { OracleHeader } from '../components/OracleHeader';
import { ChevronDown, Filter, Download, RefreshCw } from 'lucide-react';

interface Opportunity {
    opp_id: string;
    opp_number: string;
    opp_name: string;
    customer_name: string;
    sales_owner: string;
    practice: string;
    status: string;
    creation_date: string;
    account_owner: string;
    deal_value: number;
    estimated_billing: string;
    sales_stage: string;
    region: string;
    win_probability?: number;
}

interface DashboardMetrics {
    totalOpportunities: number;
    totalValue: number;
    avgWinProbability: number;
    pendingApprovals: number;
}

export const ManagementDashboard: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [metrics, setMetrics] = useState<DashboardMetrics>({
        totalOpportunities: 0,
        totalValue: 0,
        avgWinProbability: 0,
        pendingApprovals: 0
    });
    const [loading, setLoading] = useState(true);
    const [selectedView, setSelectedView] = useState('All Opportunities');
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/inbox/unassigned');
            const data = await response.json();
            setOpportunities(data);

            // Calculate metrics
            const total = data.length;
            const totalVal = data.reduce((sum: number, opp: Opportunity) => sum + (opp.deal_value || 0), 0);
            const avgWin = data.reduce((sum: number, opp: Opportunity) => sum + (opp.win_probability || 100), 0) / (total || 1);

            setMetrics({
                totalOpportunities: total,
                totalValue: totalVal,
                avgWinProbability: Math.round(avgWin),
                pendingApprovals: Math.floor(total * 0.3) // Mock: 30% pending
            });
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const getWinProbabilityClass = (prob?: number) => {
        if (!prob) return 'high';
        if (prob >= 70) return 'high';
        if (prob >= 40) return 'medium';
        return 'low';
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const formatLargeNumber = (num: number) => {
        if (num >= 1000000) {
            return `$${(num / 1000000).toFixed(1)}M`;
        }
        if (num >= 1000) {
            return `$${(num / 1000).toFixed(0)}K`;
        }
        return `$${num}`;
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: 'white' }}>
            <OracleHeader />

            {/* Page Title */}
            <div className="oracle-page-title">
                <h1>Executive Dashboard</h1>
            </div>

            {/* Metrics Cards */}
            <div style={{
                padding: '24px',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '16px',
                backgroundColor: '#FAFAFA',
                borderBottom: '1px solid #E0E0E0'
            }}>
                <MetricCard
                    title="Total Opportunities"
                    value={metrics.totalOpportunities.toString()}
                    subtitle="Active in pipeline"
                    color="#1976D2"
                />
                <MetricCard
                    title="Pipeline Value"
                    value={formatLargeNumber(metrics.totalValue)}
                    subtitle={formatCurrency(metrics.totalValue)}
                    color="#2E7D32"
                />
                <MetricCard
                    title="Avg Win Probability"
                    value={`${metrics.avgWinProbability}%`}
                    subtitle="Across all opportunities"
                    color="#F57C00"
                />
                <MetricCard
                    title="Pending Approvals"
                    value={metrics.pendingApprovals.toString()}
                    subtitle="Awaiting your review"
                    color="#C62828"
                />
            </div>

            {/* Toolbar */}
            <div className="oracle-toolbar">
                <div className="oracle-search-group">
                    <button
                        className="oracle-btn"
                        onClick={() => setShowFilters(!showFilters)}
                    >
                        <Filter size={16} />
                        Filters
                    </button>
                </div>

                <div className="oracle-search-group">
                    <label className="oracle-search-label">View</label>
                    <select
                        className="oracle-select"
                        value={selectedView}
                        onChange={(e) => setSelectedView(e.target.value)}
                    >
                        <option>All Opportunities</option>
                        <option>High Value (&gt;$1M)</option>
                        <option>Pending Initial Review</option>
                        <option>Pending Final Approval</option>
                        <option>Approved This Month</option>
                    </select>
                </div>

                <div className="oracle-toolbar-spacer"></div>

                <button className="oracle-btn" onClick={fetchDashboardData}>
                    <RefreshCw size={16} />
                    Refresh
                </button>

                <button className="oracle-btn">
                    <Download size={16} />
                    Export
                </button>
            </div>

            {/* Filter Panel */}
            {showFilters && (
                <div style={{
                    padding: '16px 24px',
                    backgroundColor: '#F5F5F5',
                    borderBottom: '1px solid #E0E0E0',
                    display: 'flex',
                    gap: '16px',
                    flexWrap: 'wrap'
                }}>
                    <div>
                        <label style={{ fontSize: '12px', color: '#757575', display: 'block', marginBottom: '4px' }}>
                            Practice
                        </label>
                        <select className="oracle-select" style={{ minWidth: '150px' }}>
                            <option>All Practices</option>
                            <option>IAM - Cybertech</option>
                            <option>Cloud Services</option>
                            <option>Security</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ fontSize: '12px', color: '#757575', display: 'block', marginBottom: '4px' }}>
                            Region
                        </label>
                        <select className="oracle-select" style={{ minWidth: '150px' }}>
                            <option>All Regions</option>
                            <option>MEA - Saudi Arabia</option>
                            <option>MEA - Dubai</option>
                            <option>ASEAN</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ fontSize: '12px', color: '#757575', display: 'block', marginBottom: '4px' }}>
                            Status
                        </label>
                        <select className="oracle-select" style={{ minWidth: '150px' }}>
                            <option>All Statuses</option>
                            <option>Committed</option>
                            <option>Forecast</option>
                            <option>Pipeline</option>
                        </select>
                    </div>

                    <div>
                        <label style={{ fontSize: '12px', color: '#757575', display: 'block', marginBottom: '4px' }}>
                            Sales Stage
                        </label>
                        <select className="oracle-select" style={{ minWidth: '150px' }}>
                            <option>All Stages</option>
                            <option>PO Received</option>
                            <option>Proposal</option>
                            <option>Negotiation</option>
                        </select>
                    </div>
                </div>
            )}

            {/* View Selector */}
            <div className="oracle-view-selector">
                <label className="oracle-view-label">Columns</label>
                <button className="oracle-icon-btn">
                    <ChevronDown size={16} />
                </button>
            </div>

            {/* Table */}
            <div className="oracle-table-container">
                {loading ? (
                    <div className="oracle-loading">
                        <p>Loading dashboard data...</p>
                    </div>
                ) : opportunities.length === 0 ? (
                    <div className="oracle-empty">
                        <div className="oracle-empty-icon">📊</div>
                        <p>No opportunities found</p>
                    </div>
                ) : (
                    <table className="oracle-table">
                        <thead>
                            <tr>
                                <th style={{ width: '60px' }}>Win (%)</th>
                                <th>Opportunity Nbr</th>
                                <th>Name</th>
                                <th>Owner</th>
                                <th>Practice</th>
                                <th>Status</th>
                                <th>Creation Date</th>
                                <th>Account</th>
                                <th>Account Owner</th>
                                <th className="text-right">Amount</th>
                                <th>Estimated Billing</th>
                                <th>Sales Stage</th>
                                <th>Region</th>
                            </tr>
                        </thead>
                        <tbody>
                            {opportunities.map((opp) => (
                                <tr key={opp.opp_id}>
                                    <td>
                                        <span className={`oracle-win-badge ${getWinProbabilityClass(opp.win_probability)}`}>
                                            {opp.win_probability || 100}
                                        </span>
                                    </td>
                                    <td>{opp.opp_number}</td>
                                    <td>
                                        <a className="oracle-link">
                                            {opp.opp_name}
                                        </a>
                                    </td>
                                    <td>{opp.sales_owner || 'Kamal AL Al Safi'}</td>
                                    <td>{opp.practice || 'IAM - Cybertech'}</td>
                                    <td>
                                        <span className={`oracle-status-badge ${opp.status?.toLowerCase() || 'committed'}`}>
                                            {opp.status || 'Committed'}
                                        </span>
                                    </td>
                                    <td>{formatDate(opp.creation_date)}</td>
                                    <td>{opp.customer_name}</td>
                                    <td>{opp.account_owner || opp.sales_owner}</td>
                                    <td className="text-right">{formatCurrency(opp.deal_value || 0)}</td>
                                    <td>{opp.estimated_billing || formatDate(opp.creation_date)}</td>
                                    <td>{opp.sales_stage || 'PO Received'}</td>
                                    <td>{opp.region || 'MEA - Saudi Arabia'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

// Metric Card Component
interface MetricCardProps {
    title: string;
    value: string;
    subtitle: string;
    color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, color }) => {
    return (
        <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #E0E0E0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
            <div style={{
                fontSize: '12px',
                color: '#757575',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                fontWeight: 600
            }}>
                {title}
            </div>
            <div style={{
                fontSize: '32px',
                fontWeight: 600,
                color: color,
                marginBottom: '4px'
            }}>
                {value}
            </div>
            <div style={{
                fontSize: '12px',
                color: '#757575'
            }}>
                {subtitle}
            </div>
        </div>
    );
};
