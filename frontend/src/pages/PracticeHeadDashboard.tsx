import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search, TrendingUp } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable } from '../components/OpportunitiesTable';

type TabType = 'action-required' | 'all' | 'unassigned' | 'assigned' | 'under-assessment' | 'approved' | 'rejected' | 'metrics';

export function PracticeHeadDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const location = useLocation();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('action-required');
    const [viewMode, setViewMode] = useState('All Opportunities');

    // Sync URL with Tab
    useEffect(() => {
        const path = location.pathname;
        if (path.includes('action-required')) setActiveTab('action-required');
        else if (path.includes('unassigned')) setActiveTab('unassigned');
        else if (path.includes('assign')) setActiveTab('assigned');
        else if (path.includes('review')) setActiveTab('under-assessment');
        else if (path.includes('metrics')) setActiveTab('metrics');
        else setActiveTab('action-required');
    }, [location.pathname]);

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<number[]>([]);

    // Action menu state
    const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);

    useEffect(() => {
        fetchOpportunities();
    }, []);

    const fetchOpportunities = () => {
        console.log('🔄 Fetching opportunities...');
        setLoading(true);
        fetch('http://127.0.0.1:8000/api/opportunities/')
            .then(res => {
                console.log('📡 Response status:', res.status);
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                console.log('✅ Received data count:', data.length);
                console.log('📊 First 3 items:', data.slice(0, 3));
                setOpportunities(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("❌ Failed to fetch opportunities:", err);
                alert(`Failed to load opportunities: ${err.message}`);
                setLoading(false);
            });
    };

    // --- Metrics Calculations ---
    const totalOpps = opportunities.length;
    const pipelineValue = opportunities.reduce((sum, o) => sum + (o.deal_value || 0), 0);
    const avgWinProb = totalOpps > 0 ? Math.round(opportunities.reduce((sum, o) => sum + (o.win_probability || 0), 0) / totalOpps) : 0;

    // --- 1. Efficient Client-Side Bucketing (useMemo) ---
    // Safely normalize status for comparison
    const normStatus = (o: Opportunity) => (o.workflow_status || '').toUpperCase();

    const unassignedOpportunities = React.useMemo(() =>
        opportunities.filter(o => {
            const s = normStatus(o);
            // Strict logic: Status is NEW or null/empty or OPEN
            // Explicit check for OPEN/null
            return s === 'NEW' || s === '' || s === 'OPEN';
        }),
        [opportunities]);

    const assignedOpportunities = React.useMemo(() =>
        opportunities.filter(o => normStatus(o) === 'ASSIGNED_TO_SA'),
        [opportunities]);

    const assessmentOpportunities = React.useMemo(() =>
        opportunities.filter(o => normStatus(o) === 'UNDER_ASSESSMENT'),
        [opportunities]);

    const reviewOpportunities = React.useMemo(() =>
        opportunities.filter(o => normStatus(o) === 'SUBMITTED_FOR_REVIEW'),
        [opportunities]);

    const acceptedOpportunities = React.useMemo(() =>
        opportunities.filter(o => ['APPROVED', 'ACCEPTED', 'COMPLETED', 'WON'].includes(normStatus(o))),
        [opportunities]);

    const rejectedOpportunities = React.useMemo(() =>
        opportunities.filter(o => ['REJECTED', 'LOST'].includes(normStatus(o))),
        [opportunities]);

    // Derived counts for UI
    const statusCounts = {
        NEW: unassignedOpportunities.length,
        ASSIGNED: assignedOpportunities.length + assessmentOpportunities.length, // Grouping for high-level pipeline view if needed
        ASSESSMENT: assessmentOpportunities.length,
        REVIEW: reviewOpportunities.length,
        ACCEPTED: acceptedOpportunities.length,
        REJECTED: rejectedOpportunities.length
    };

    const awaitingReviewCount = reviewOpportunities.length;

    const TAB_LABELS: Record<string, string> = {
        'action-required': 'Action Required',
        'all': 'All Entities',
        'unassigned': 'Unassigned',
        'assigned': 'Assigned to SA',
        'under-assessment': 'Under-Assessment',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'metrics': 'Practice Metrics'
    };

    // --- Filtering for Display ---
    const getFilteredOpportunities = () => {
        // Simple switch to return the pre-calculated bucket
        switch (activeTab) {
            case 'action-required':
                return [...unassignedOpportunities, ...reviewOpportunities];
            case 'unassigned':
                return unassignedOpportunities;
            case 'assigned':
                return assignedOpportunities;
            case 'under-assessment':
                // Combine under-assessment and review for this view context if preferred, 
                // or just assessment. The logic in Step 80 combined them in 'assigned' check? 
                // Wait, previous code:
                // case 'under-assessment': status === 'UNDER_ASSESSMENT' || 'SUBMITTED_FOR_REVIEW'
                // Let's keep that broader definition for this tab if desired, or separate them.
                // The user asked for "Divide it into stages... New, Assigned, Submitted, Accepted, Rejected"
                // Let's stick to the buckets strictly.
                // But the tab name 'under-assessment' usually implies work in progress. 
                // Let's include both for continuity or just assessment. 
                // Given the bucket lists:
                return [...assessmentOpportunities, ...reviewOpportunities];
            case 'approved':
                return acceptedOpportunities;
            case 'rejected':
                return rejectedOpportunities;
            case 'metrics':
                return [];
            case 'all':
            default:
                return opportunities;
        }
    };
    const filteredOpportunities = getFilteredOpportunities();

    // Helper needed for the "Action Required" view which iterates separately
    // We can just check inclusion in unassignedOpportunities
    const isUnassigned = (o: Opportunity) => {
        const s = normStatus(o);
        // Explicit check for OPEN/null
        return s === 'NEW' || s === '' || s === 'OPEN';
    };

    const handleAssignToSA = async (oppId: number, primarySA: string, secondarySA?: string) => {
        try {
            console.log('🔄 Assigning opportunity:', oppId, 'to SA:', primarySA);

            const res = await fetch('http://127.0.0.1:8000/api/inbox/assign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    opp_id: oppId.toString(),
                    sa_email: primarySA,
                    assigned_by_user_id: user?.id || 'PRACTICE_HEAD'
                })
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || "Assignment failed");
            }

            const result = await res.json();
            console.log('✅ Assignment successful:', result);

            // Optimistic UI update: Update the opportunity in state immediately
            setOpportunities(prevOpps =>
                prevOpps.map(opp =>
                    opp.id === oppId
                        ? { ...opp, assigned_sa: result.opportunity.assigned_sa, workflow_status: result.opportunity.workflow_status }
                        : opp
                )
            );

            // Close modal
            setIsAssignModalOpen(false);

            // Refetch to ensure consistency with backend
            setTimeout(() => fetchOpportunities(), 100);

        } catch (err) {
            console.error('❌ Assignment error:', err);
            alert(`Failed to assign architect: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
    };

    const handleApprove = async (oppId: number) => {
        if (!confirm("Approve this assessment?")) return;
        try {
            await fetch(`http://127.0.0.1:8000/api/scoring/${oppId}/review/approve`, { method: 'POST' });
            fetchOpportunities();
        } catch (e) {
            console.error(e);
            alert("Approval failed");
        }
    };

    const handleReject = async (oppId: number) => {
        const reason = prompt("Enter rejection reason:");
        if (!reason) return;
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/scoring/${oppId}/review/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason })
            });
            if (!res.ok) throw new Error("Rejection failed");
            fetchOpportunities();
        } catch (e) {
            console.error(e);
            alert("Rejection failed");
        }
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
    const formatLargeNumber = (num: number) => {
        if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `$${(num / 1000).toFixed(0)}K`;
        return `$${num}`;
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900 overflow-x-hidden">
            <TopBar title="Practice Head Dashboard" />

            <div className="flex-1 px-4 py-4 w-full">

                {/* Header with Title */}
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-normal text-[#333333]">Opportunities</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-500 cursor-help">?</div>
                    </div>
                </div>

                {/* Metrics Grid - Oracle Style */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    {/* Card 1 - Total Opportunities */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">TOTAL OPPORTUNITIES</div>
                        <div>
                            <div className="text-4xl font-normal text-[#0572CE]">{totalOpps}</div>
                            <div className="text-[11px] text-[#666666] mt-1">Active in pipeline</div>
                        </div>
                    </div>

                    {/* Card 2 - Pipeline Value */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">PIPELINE VALUE</div>
                        <div>
                            <div className="text-4xl font-normal text-[#217346]">{formatLargeNumber(pipelineValue)}</div>
                            <div className="text-[11px] text-[#666666] mt-1">{formatCurrency(pipelineValue)}</div>
                        </div>
                    </div>

                    {/* Card 3 - Avg Win Probability */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">AVG WIN PROBABILITY</div>
                        <div>
                            <div className="text-4xl font-normal text-[#E27D12]">{avgWinProb}%</div>
                            <div className="text-[11px] text-[#666666] mt-1">Across all opportunities</div>
                        </div>
                    </div>

                    {/* Card 4 - Pending Actions */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">PENDING ACTIONS</div>
                        <div>
                            <div className="text-4xl font-normal text-[#C74634]">{awaitingReviewCount}</div>
                            <div className="text-[11px] text-[#666666] mt-1">Awaiting your review</div>
                        </div>
                    </div>
                </div>

                {/* Toolbar - Oracle CRM Style */}
                <div className="flex items-center justify-between py-2 mb-4">
                    <div className="flex items-center gap-4">
                        {/* Filters */}
                        <button className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-normal text-[#333333] border border-gray-300 rounded bg-white hover:bg-gray-50">
                            <Filter size={14} /> Filters
                        </button>

                        {/* Find */}
                        <div className="flex items-center gap-2">
                            <span className="text-[13px] text-[#333333]">Find</span>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Name"
                                    className="border border-gray-300 rounded px-2 py-1.5 text-[13px] w-48 focus:outline-none focus:border-[#0572CE] bg-white"
                                />
                                <Search size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 cursor-pointer" />
                            </div>
                        </div>

                        {/* List */}
                        <div className="flex items-center gap-2">
                            <span className="text-[13px] text-[#333333]">List</span>
                            <div className="relative">
                                <select
                                    className="appearance-none border border-gray-300 rounded pl-3 pr-8 py-1.5 text-[13px] font-normal text-[#333333] bg-white focus:outline-none"
                                    value={viewMode}
                                    onChange={(e) => setViewMode(e.target.value)}
                                >
                                    <option>All Opportunities</option>
                                    <option>My Opportunities</option>
                                </select>
                                <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
                            </div>
                        </div>

                        {/* Menu Toggle */}
                        <button className="p-1.5 hover:bg-gray-100 rounded">
                            <MoreHorizontal size={18} className="text-gray-600 rotate-90" />
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        {/* Refresh */}
                        <button
                            onClick={fetchOpportunities}
                            className="flex items-center gap-2 px-4 py-1.5 text-[13px] font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50"
                        >
                            <RefreshCw size={14} /> Refresh
                        </button>

                        {/* Actions Dropdown */}
                        <div className="relative">
                            <button
                                onClick={() => setOpenActionMenu(openActionMenu === -999 ? null : -999)}
                                className="flex items-center gap-2 px-4 py-1.5 text-[13px] font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50"
                            >
                                Actions <ChevronDown size={12} />
                            </button>

                            {openActionMenu === -999 && (
                                <div className="absolute right-0 mt-1 w-56 bg-white rounded shadow-lg border border-gray-200 z-50 py-1">
                                    <button
                                        onClick={() => {
                                            const selected = opportunities.filter(o => o.workflow_status === 'SUBMITTED_FOR_REVIEW');
                                            if (selected.length > 0) handleApprove(selected[0].id);
                                            setOpenActionMenu(null);
                                        }}
                                        className="w-full text-left px-4 py-2 text-sm text-[#00695c] hover:bg-gray-50 flex items-center gap-2"
                                    >
                                        <CheckCircle size={14} /> Approve Selected
                                    </button>
                                    <button
                                        onClick={() => {
                                            const selected = opportunities.filter(o => o.workflow_status === 'SUBMITTED_FOR_REVIEW');
                                            if (selected.length > 0) handleReject(selected[0].id);
                                            setOpenActionMenu(null);
                                        }}
                                        className="w-full text-left px-4 py-2 text-sm text-[#C62828] hover:bg-gray-50 flex items-center gap-2"
                                    >
                                        <XCircle size={14} /> Reject Selected
                                    </button>
                                    <div className="border-t border-gray-100 my-1"></div>
                                    <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                                        <Download size={14} /> Export to CSV
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Create Button */}
                        <button className="px-4 py-1.5 text-[13px] font-normal text-white bg-[#0572CE] rounded hover:bg-[#005a9e]">
                            Create Opportunity
                        </button>
                    </div>
                </div>

                {/* Opportunities Table */}
                <div className="mt-6">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-[13px] text-[#333333]">View</span>
                        <ChevronDown size={14} className="text-gray-500" />
                    </div>
                    <OpportunitiesTable
                        opportunities={filteredOpportunities}
                        loading={loading}
                        onAssign={(opp) => {
                            setSelectedOppId([opp.id]);
                            setIsAssignModalOpen(true);
                        }}
                        onApprove={handleApprove}
                        onReject={handleReject}
                        onView={(id) => navigate(`/opportunity/${id}`)}
                        formatCurrency={formatCurrency}
                    />
                    {/* Modals */}
                    <AssignArchitectModal
                        isOpen={isAssignModalOpen}
                        onClose={() => setIsAssignModalOpen(false)}
                        opportunityIds={selectedOppId}
                        onAssign={(data: AssignmentData) => {
                            handleAssignToSA(selectedOppId[0], data.sa_owner, data.secondary_sa);
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
