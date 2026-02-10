import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { ApprovalModal } from '../components/ApprovalModal';

type TabType = 'unassigned' | 'assigned' | 'under-assessment' | 'pending-review' | 'completed' | 'accepted' | 'rejected' | 'all';

export function ManagementDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();

    // Data State
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [totalValue, setTotalValue] = useState(0);
    const [tabCounts, setTabCounts] = useState<Record<string, number>>({});

    // UI State
    const [activeTab, setActiveTab] = useState<TabType>('unassigned');
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [assignTargetRole, setAssignTargetRole] = useState<'PH' | 'SH' | 'SP'>('PH');
    const [selectedOppId, setSelectedOppId] = useState<string[]>([]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
            setCurrentPage(1);
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    // Fetch opportunities
    useEffect(() => {
        fetchOpportunities();
    }, [currentPage, pageSize, debouncedSearch, activeTab]);

    const fetchOpportunities = () => {
        setLoading(true);
        const params = new URLSearchParams({
            page: currentPage.toString(),
            limit: pageSize.toString(),
            tab: activeTab,
            user_id: user?.id || '',
            role: user?.role || ''
        });
        if (debouncedSearch) params.append('search', debouncedSearch);

        fetch(`http://127.0.0.1:8000/api/opportunities?${params}`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.items && Array.isArray(data.items)) {
                    setOpportunities(data.items);
                    setTotalCount(data.total_count || 0);
                    setTotalValue(data.total_value || 0);
                    if (data.counts) setTabCounts(data.counts);
                } else if (Array.isArray(data)) {
                    setOpportunities(data);
                } else {
                    console.error("Unexpected API response format:", data);
                    setOpportunities([]);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setOpportunities([]);
                setLoading(false);
            });
    };

    const openAssignModal = (id: string, role: 'PH' | 'SH' | 'SP') => {
        console.log('🔵 Opening assign modal:', { id, role });
        setSelectedOppId([id]);
        setAssignTargetRole(role);
        setIsAssignModalOpen(true);
        console.log('🔵 Modal state set to true');
    };

    const handleAssign = async (assignment: AssignmentData) => {
        const userId = assignment.sa_owner;
        try {
            await Promise.all(selectedOppId.map(id =>
                fetch(`http://127.0.0.1:8000/api/opportunities/${id}/assign`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: assignTargetRole,
                        user_id: userId,
                        assigned_by: user?.role
                    })
                })
            ));
            fetchOpportunities();
            setIsAssignModalOpen(false);
            setSelectedOppId([]);
        } catch (e) {
            console.error(e);
            alert("Assignment failed.");
        }
    };


    // Removed old handleApprove and handleReject

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    const getTabCount = (tab: TabType) => {
        const backendKey = tab === 'pending-review' ? 'review' : tab;
        return tabCounts[backendKey] || 0;
    };

    const avgWinProb = opportunities.length > 0 ? Math.round(opportunities.reduce((sum, o) => sum + (o.win_probability || 0), 0) / opportunities.length) : 0;

    // Approval Modal State
    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
    const [approvalAction, setApprovalAction] = useState<'APPROVE' | 'REJECT' | null>(null);
    const [approvalOppId, setApprovalOppId] = useState<string | null>(null);

    const openApprovalModal = (id: string, action: 'APPROVE' | 'REJECT') => {
        setApprovalOppId(id);
        setApprovalAction(action);
        setIsApprovalModalOpen(true);
    };

    const handleModalConfirm = async (comment: string) => {
        if (!approvalOppId || !approvalAction) return;

        try {
            await fetch(`http://127.0.0.1:8000/api/opportunities/${approvalOppId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role: 'GH',
                    decision: approvalAction,
                    user_id: user?.id,
                    comment: comment
                })
            });
            fetchOpportunities();
            setIsApprovalModalOpen(false);
        } catch (e) {
            console.error(e);
            alert(`Failed to ${approvalAction.toLowerCase()}`);
        }
    };

    // --- filtering for Display ---
    const filteredOpportunities = opportunities; // Backend filtering handles this

    const handleAssignClick = (opp: Opportunity, type?: 'PH' | 'SH' | 'SA' | 'SP') => {
        if (type) {
            setSelectedOppId([opp.id]);
            setAssignTargetRole(type as 'PH' | 'SH' | 'SP');
            setIsAssignModalOpen(true);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-[#f3f4f6]">
            <TopBar />
            <div className="flex-1 overflow-hidden flex flex-col">
                {/* Metrics Header */}
                <div className="bg-white px-8 py-6 border-b border-gray-200 shadow-sm">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-2xl font-bold text-[#333333] tracking-tight">Management Dashboard</h1>
                            <p className="text-sm text-gray-500 mt-1">Overview of opportunity pipeline and team performance</p>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 text-xs font-semibold rounded-full border border-green-100">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            Oracle CRM Connected
                        </div>
                    </div>

                    <div className="grid grid-cols-4 gap-6">
                        <div className="bg-gradient-to-br from-blue-50 to-white p-4 rounded-xl border border-blue-100 shadow-sm">
                            <div className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Total Pipeline</div>
                            <div className="text-2xl font-black text-gray-900">{totalCount}</div>
                            <div className="text-xs text-gray-500 mt-1">Active Opportunities</div>
                        </div>
                        <div className="bg-gradient-to-br from-indigo-50 to-white p-4 rounded-xl border border-indigo-100 shadow-sm">
                            <div className="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-1">Pipeline Value</div>
                            <div className="text-2xl font-black text-gray-900">{formatCurrency(totalValue)}</div>
                            <div className="text-xs text-gray-500 mt-1">Total Potential Revenue</div>
                        </div>
                        <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-xl border border-purple-100 shadow-sm">
                            <div className="text-xs font-bold text-purple-600 uppercase tracking-wider mb-1">Avg. Win Prob</div>
                            <div className="text-2xl font-black text-gray-900">{avgWinProb}%</div>
                            <div className="text-xs text-gray-500 mt-1">Based on AI Scoring</div>
                        </div>
                        <div className="bg-gradient-to-br from-amber-50 to-white p-4 rounded-xl border border-amber-100 shadow-sm cursor-pointer" onClick={() => setActiveTab('pending-review')}>
                            <div className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-1">Action Required</div>
                            <div className="text-2xl font-black text-gray-900">{getTabCount('pending-review')}</div>
                            <div className="text-xs text-gray-500 mt-1">Pending Review</div>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 bg-white px-4 pt-2 shadow-sm">
                    {['unassigned', 'pending-review', 'completed', 'all'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab as TabType)}
                            className={`px-4 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors whitespace-nowrap ${activeTab === tab
                                ? 'border-[#0073BB] text-[#0073BB]'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            {tab.replace('-', ' ')} ({getTabCount(tab as TabType)})
                        </button>
                    ))}
                </div>

                {/* Toolbar */}
                <div className="flex items-center justify-between bg-white p-4 border-b border-gray-200 shadow-sm">
                    <div className="flex items-center gap-6">
                        {selectedOppId.length > 0 ? (
                            <>
                                <div className="flex items-center gap-3 px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
                                    <span className="text-sm font-bold text-blue-900">{selectedOppId.length} selected</span>
                                    <button
                                        onClick={() => setSelectedOppId([])}
                                        className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
                                    >
                                        Clear
                                    </button>
                                </div>
                                {user?.role === 'GH' && (
                                    <>
                                        <button
                                            onClick={() => {
                                                setAssignTargetRole('PH');
                                                setIsAssignModalOpen(true);
                                            }}
                                            className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm transition-all"
                                        >
                                            Assign to Practice Head
                                        </button>
                                        <button
                                            onClick={() => {
                                                setAssignTargetRole('SH');
                                                setIsAssignModalOpen(true);
                                            }}
                                            className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-indigo-600 rounded hover:bg-indigo-700 shadow-sm transition-all"
                                        >
                                            Assign to Sales Head
                                        </button>
                                    </>
                                )}
                            </>
                        ) : (
                            <>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-normal text-[#666666]">Find</span>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            placeholder="Search name, client, or ID..."
                                            className="border border-gray-300 rounded px-4 py-2 w-64 text-sm focus:outline-none focus:ring-1 focus:ring-[#0073BB]"
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                        />
                                        <Search size={18} className="absolute right-3 top-2.5 text-[#666666]" />
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    <div className="flex items-center gap-3">
                        <button onClick={fetchOpportunities} className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50">
                            <RefreshCw size={18} className="text-[#666666]" /> Refresh
                        </button>
                    </div>
                </div>

                {/* Table */}
                <div className="flex-1 overflow-auto bg-white border border-gray-200 shadow-sm px-4">
                    <OpportunitiesTable
                        opportunities={filteredOpportunities}
                        loading={loading}
                        onAssign={handleAssignClick}
                        onApprove={(id) => openApprovalModal(id, 'APPROVE')}
                        onReject={(id) => openApprovalModal(id, 'REJECT')}
                        onView={(id, jumpToScore) => {
                            if (jumpToScore) navigate(`/score/${id}`);
                            else navigate(`/opportunity/${id}`);
                        }}
                        formatCurrency={formatCurrency}
                        selectedIds={selectedOppId}
                        onSelectionChange={setSelectedOppId}
                        role="GH"
                    />
                </div>

                {/* Pagination */}
                <div className="mt-4 flex items-center justify-between bg-white px-8 py-4 rounded-xl border border-gray-200 shadow-sm mb-4 mx-4">
                    <div className="text-sm text-gray-500">
                        Showing <span className="font-bold text-gray-900">{opportunities.length}</span> of <span className="font-bold text-gray-900">{totalCount}</span> opportunities
                    </div>
                    {/* Pagination control reuse */}
                    <div className="flex items-center gap-2">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage(prev => prev - 1)}
                            className="px-4 py-2 text-sm font-bold border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            Previous
                        </button>
                        <span className="text-sm text-gray-600">Page {currentPage} of {Math.ceil(totalCount / pageSize) || 1}</span>
                        <button
                            disabled={currentPage >= Math.ceil(totalCount / pageSize)}
                            onClick={() => setCurrentPage(prev => prev + 1)}
                            className="px-4 py-2 text-sm font-bold border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>

            {/* Modals */}
            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                opportunityIds={selectedOppId}
                targetRole={assignTargetRole}
                title={
                    assignTargetRole === 'PH' ? "Assign Practice Head" :
                        assignTargetRole === 'SH' ? "Assign Sales Head" :
                            "Assign Sales Presales"
                }
                onAssign={handleAssign}
            />

            <ApprovalModal
                isOpen={isApprovalModalOpen}
                onClose={() => setIsApprovalModalOpen(false)}
                onConfirm={handleModalConfirm}
                type={approvalAction || 'APPROVE'}
            />
        </div>
    );
}
