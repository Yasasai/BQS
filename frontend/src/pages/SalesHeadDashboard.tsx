import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search, TrendingUp, Users } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ManageUsersModal } from '../components/ManageUsersModal';
import { ApprovalModal } from '../components/ApprovalModal';

type TabType = 'action-required' | 'in-progress' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'action-required': 'Action Required',
    'in-progress': 'In Progress',
    'review': 'Review',
    'completed': 'Completed'
};

export function SalesHeadDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const location = useLocation();

    // Data State
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [globalPipelineValue, setGlobalPipelineValue] = useState(0);
    const [tabCounts, setTabCounts] = useState<Record<string, number>>({});

    // Pagination & Search State
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(50);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    const [activeTab, setActiveTab] = useState<TabType>('action-required');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [isUserModalOpen, setIsUserModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<string[]>([]);

    // Role-based Access Control
    useEffect(() => {
        if (user?.role !== 'SH' && user?.role !== 'GH') {
            // Redirect if not SH (admin GH can view too ideally, but for now stick to role)
            if (user?.role === 'PH') navigate('/practice-head/dashboard');
            if (user?.role === 'SA') navigate('/assigned-to-me');
        }
    }, [user, navigate]);

    // Sync URL with Tab
    useEffect(() => {
        const path = location.pathname;
        if (path.includes('action-required')) setActiveTab('action-required');
        else if (path.includes('in-progress')) setActiveTab('in-progress');
        else if (path.includes('review')) setActiveTab('review');
        else if (path.includes('completed')) setActiveTab('completed');
        else setActiveTab('action-required');
    }, [location.pathname]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
            setCurrentPage(1); // Reset to page 1 on search
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    // Fetch on changes
    useEffect(() => {
        fetchOpportunities();
        setSelectedOppId([]); // Clear selection when tab/page/search changes
    }, [currentPage, pageSize, debouncedSearch, activeTab]);

    const fetchOpportunities = () => {
        console.log('🔄 Fetching opportunities page:', currentPage, 'Tab:', activeTab);
        setLoading(true);

        const params = new URLSearchParams({
            page: currentPage.toString(),
            limit: pageSize.toString(),
            tab: activeTab,
            user_id: user?.id || '',
            role: user?.role || ''
        });
        if (debouncedSearch) params.append('search', debouncedSearch);

        fetch(`http://127.0.0.1:8000/api/opportunities/?${params}`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.items) {
                    setOpportunities(data.items);
                    setTotalCount(data.total_count);
                    setGlobalPipelineValue(data.total_value || 0);
                    if (data.counts) setTabCounts(data.counts);
                } else {
                    setOpportunities(data);
                    setTotalCount(data.length);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("❌ Failed to fetch opportunities:", err);
                setLoading(false);
            });
    };


    // --- filtering for Display ---
    const filteredOpportunities = opportunities;

    const handleAssignToSP = async (oppIds: string | string[], primarySP: string, secondarySP?: string) => {
        const idsToAssign = Array.isArray(oppIds) ? oppIds : [oppIds];
        try {
            await Promise.all(idsToAssign.map(id =>
                fetch(`http://127.0.0.1:8000/api/opportunities/${id}/assign`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: 'SP',
                        user_id: primarySP,
                        assigned_by: user?.id || 'SALES_HEAD'
                    })
                })
            ));
            fetchOpportunities();
            setIsAssignModalOpen(false);
            setSelectedOppId([]);
        } catch (err) {
            console.error('❌ Assignment error:', err);
            alert(`Failed to assign: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
    };


    // --- Approval Modal Logic ---
    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
    const [approvalAction, setApprovalAction] = useState<'APPROVE' | 'REJECT' | null>(null);
    const [approvalIds, setApprovalIds] = useState<string[]>([]);

    const openApprovalModal = (ids: string | string[], action: 'APPROVE' | 'REJECT') => {
        setApprovalIds(Array.isArray(ids) ? ids : [ids]);
        setApprovalAction(action);
        setIsApprovalModalOpen(true);
    };

    const handleModalConfirm = async (comment: string) => {
        if (approvalIds.length === 0 || !approvalAction) return;

        try {
            await Promise.all(approvalIds.map(id =>
                fetch(`http://127.0.0.1:8000/api/opportunities/${id}/approve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: 'SH',
                        decision: approvalAction,
                        user_id: user?.id,
                        comment: comment
                    })
                })
            ));
            fetchOpportunities();
            setSelectedOppId([]);
            setIsApprovalModalOpen(false);
        } catch (error) {
            console.error(error);
            alert("Action failed.");
        }
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900 overflow-x-hidden">
            <TopBar title="Sales Head Dashboard" />
            <div className="flex-1 px-4 py-4 w-full max-w-[1600px] mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-normal text-[#333333]">Opportunities</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-500 cursor-help">?</div>
                    </div>
                </div>


                {/* Tab Switcher */}
                <div className="flex items-center gap-8 border-b border-gray-200 mb-6 mt-4">
                    {(Object.keys(TAB_LABELS) as TabType[])
                        .map((tabId) => (
                            <button
                                key={tabId}
                                onClick={() => navigate(`/sales/${tabId}`)}
                                className={`pb-3 text-sm font-medium transition-all relative ${activeTab === tabId
                                    ? 'text-[#0572CE]'
                                    : 'text-[#666666] hover:text-[#333333]'
                                    }`}
                            >
                                {TAB_LABELS[tabId]} ({tabCounts[tabId] || 0})
                                {activeTab === tabId && (
                                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0572CE]" />
                                )}
                            </button>
                        ))}
                </div>


                <div className="flex items-center justify-between py-3 mb-4 px-4 bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div className="flex items-center gap-4">
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
                                <button
                                    onClick={() => setIsAssignModalOpen(true)}
                                    className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm transition-all"
                                >
                                    <UserPlus size={16} />
                                    Assign to Sales Person
                                </button>
                                {(() => {
                                    const selectedItems = opportunities.filter(o => selectedOppId.includes(o.id));
                                    const canReview = selectedItems.length > 0 && selectedItems.every(o => {
                                        const s = (o.workflow_status || '').toUpperCase();
                                        return s === 'SUBMITTED_FOR_REVIEW' || s === 'SUBMITTED' || s === 'READY_FOR_REVIEW';
                                    });
                                    return canReview && (
                                        <>
                                            <button
                                                onClick={() => openApprovalModal(selectedOppId, 'APPROVE')}
                                                className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-green-600 rounded hover:bg-green-700 shadow-sm transition-all"
                                            >
                                                <CheckCircle size={16} />
                                                Approve Selected
                                            </button>
                                            <button
                                                onClick={() => openApprovalModal(selectedOppId, 'REJECT')}
                                                className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-red-600 rounded hover:bg-red-700 shadow-sm transition-all"
                                            >
                                                <XCircle size={16} />
                                                Reject Selected
                                            </button>
                                        </>
                                    );
                                })()}
                            </>
                        ) : (
                            <div className="flex items-center gap-2">
                                <span className="text-[13px] text-[#333333]">Find</span>
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder="Search Name, Customer..."
                                        className="border border-gray-300 rounded px-2 py-1.5 text-[13px] w-64 focus:outline-none focus:border-[#0572CE] bg-white pl-8"
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                    />
                                    <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        <button onClick={() => fetchOpportunities()} className="flex items-center gap-2 px-4 py-1.5 text-[13px] font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50">
                            <RefreshCw size={14} /> Refresh
                        </button>
                    </div>
                </div>


                <div className="flex items-center gap-2 mb-2">
                    <span className="text-[13px] text-[#333333] font-medium">{TAB_LABELS[activeTab] || 'Opportunities'}</span>
                </div>

                <OpportunitiesTable
                    opportunities={filteredOpportunities}
                    loading={loading}
                    onAssign={(opp) => { setSelectedOppId([opp.id]); setIsAssignModalOpen(true); }}
                    onApprove={(id) => openApprovalModal(id, 'APPROVE')}
                    onReject={(id) => openApprovalModal(id, 'REJECT')}
                    onView={(id, jumpToScore) => {
                        if (jumpToScore) {
                            navigate(`/score/${id}`);
                        } else {
                            navigate(`/opportunity/${id}`);
                        }
                    }}
                    formatCurrency={formatCurrency}
                    selectedIds={selectedOppId}
                    onSelectionChange={setSelectedOppId}
                    role="SH"
                />

                <div className="mt-[-48px] relative z-10">
                    <Pagination
                        currentPage={currentPage}
                        totalCount={totalCount}
                        pageSize={pageSize}
                        onPageChange={setCurrentPage}
                    />
                </div>
            </div>

            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                opportunityIds={selectedOppId}
                targetRole="SP"
                title="Assign Sales Representative"
                onAssign={(data: AssignmentData) => { handleAssignToSP(selectedOppId, data.sa_owner, data.secondary_sa); }}
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
