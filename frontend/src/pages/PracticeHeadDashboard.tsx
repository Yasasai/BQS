import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { UserPlus, CheckCircle, XCircle, RefreshCw, Search } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ManageUsersModal } from '../components/ManageUsersModal';
import { ApprovalModal } from '../components/ApprovalModal';
import { useAuth } from '../context/AuthContext';

type TabType = 'action-required' | 'in-progress' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'action-required': 'Action Required',
    'in-progress': 'In Progress',
    'review': 'Review',
    'completed': 'Completed'
};

export function PracticeHeadDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();
    const [totalCount, setTotalCount] = useState(0);
    const [tabCounts, setTabCounts] = useState<Record<string, number>>({});

    // Pagination & Search State
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(50);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    const [activeTab, setActiveTab] = useState<TabType>('action-required');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<(number | string)[]>([]);

    // Mock: In real app, get from auth context
    const currentPracticeHead = "John Doe";
    const currentPractice = "Cloud Infrastructure";

    // Role-based Access Control
    useEffect(() => {
        if (user?.role === 'SA') {
            navigate('/assigned-to-me');
        } else if (user?.role === 'GH' || user?.role === 'SH') {
            if (user?.role === 'SH') navigate('/sales/dashboard');
            else navigate('/management/dashboard');
        }
    }, [user, navigate]);

    // Sync URL with Tab
    useEffect(() => {
        const path = window.location.pathname;
        if (path.includes('action-required')) setActiveTab('action-required');
        else if (path.includes('in-progress')) setActiveTab('in-progress');
        else if (path.includes('review')) setActiveTab('review');
        else if (path.includes('completed')) setActiveTab('completed');
        else setActiveTab('action-required');
    }, [window.location.pathname]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
            setCurrentPage(1);
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

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

        fetch(`http://localhost:8000/api/opportunities/?${params}`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.items && Array.isArray(data.items)) {
                    setOpportunities(data.items);
                    setTotalCount(data.total_count || 0);
                    if (data.counts) setTabCounts(data.counts);
                } else if (Array.isArray(data)) {
                    setOpportunities(data);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    const handleAssignToSA = async (oppIds: (number | string)[], primarySA: string) => {
        try {
            await Promise.all(oppIds.map(id =>
                fetch(`http://localhost:8000/api/opportunities/${id}/assign`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: 'SA',
                        user_id: primarySA,
                        assigned_by: user?.id || 'PRACTICE_HEAD'
                    })
                })
            ));

            fetchOpportunities();
            setSelectedOppId([]);
            setIsAssignModalOpen(false);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to assign SA');
        }
    };

    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
    const [approvalAction, setApprovalAction] = useState<'APPROVE' | 'REJECT' | null>(null);
    const [approvalIds, setApprovalIds] = useState<(string | number)[]>([]);

    const openApprovalModal = (ids: (string | number) | (string | number)[], action: 'APPROVE' | 'REJECT') => {
        setApprovalIds(Array.isArray(ids) ? ids : [ids]);
        setApprovalAction(action);
        setIsApprovalModalOpen(true);
    };

    const handleModalConfirm = async (comment: string) => {
        if (approvalIds.length === 0 || !approvalAction) return;

        try {
            await Promise.all(approvalIds.map(id =>
                fetch(`http://localhost:8000/api/opportunities/${id}/approve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: 'PH',
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

    const handleApprove = (ids: (string | number)[]) => openApprovalModal(ids, 'APPROVE');
    const handleReject = (ids: (string | number)[]) => openApprovalModal(ids, 'REJECT');

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                <div className="px-8 pt-8 pb-4 bg-white border-b border-gray-200 shadow-sm">
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Practice Head Dashboard</h1>
                    <p className="text-sm text-gray-500 mt-1">Resource Allocation & Quality Assurance — {currentPractice}</p>

                    <div className="flex items-center gap-8 border-b border-gray-100 mb-0 mt-6">
                        {(Object.keys(TAB_LABELS) as TabType[])
                            .map((tabId) => (
                                <button
                                    key={tabId}
                                    onClick={() => navigate(`/practice-head/${tabId}`)}
                                    className={`pb-3 text-sm font-bold uppercase tracking-wider transition-all relative ${activeTab === tabId
                                        ? 'text-blue-600'
                                        : 'text-gray-400 hover:text-gray-600'
                                        }`}
                                >
                                    {TAB_LABELS[tabId]} ({tabCounts[tabId] || 0})
                                    {activeTab === tabId && (
                                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
                                    )}
                                </button>
                            ))}
                    </div>
                </div>

                <div className="flex-1 p-6 overflow-hidden flex flex-col">
                    <div className="flex items-center justify-between mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex items-center gap-4">
                            {selectedOppId.length > 0 ? (
                                <>
                                    <div className="flex items-center gap-3 px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
                                        <span className="text-sm font-bold text-blue-900">{selectedOppId.length} selected</span>
                                        <button onClick={() => setSelectedOppId([])} className="text-xs text-blue-600 hover:text-blue-800 font-semibold">Clear</button>
                                    </div>
                                    <button
                                        onClick={() => setIsAssignModalOpen(true)}
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-blue-600 rounded hover:bg-blue-700 shadow-sm transition-all"
                                    >
                                        <UserPlus size={16} /> Assign to SA
                                    </button>
                                    {(() => {
                                        const selectedItems = opportunities.filter(o => selectedOppId.includes(o.id));
                                        const canReview = selectedItems.length > 0 && selectedItems.every(o => {
                                            const s = (o.workflow_status || '').toUpperCase();
                                            return ['SUBMITTED_FOR_REVIEW', 'SUBMITTED', 'READY_FOR_REVIEW'].includes(s);
                                        });
                                        return canReview && (
                                            <>
                                                <button onClick={() => handleApprove(selectedOppId)} className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-green-600 rounded hover:bg-green-700 shadow-sm transition-all">
                                                    <CheckCircle size={16} /> Approve
                                                </button>
                                                <button onClick={() => handleReject(selectedOppId)} className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-red-600 rounded hover:bg-red-700 shadow-sm transition-all">
                                                    <XCircle size={16} /> Reject
                                                </button>
                                            </>
                                        );
                                    })()}
                                </>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-gray-400 font-bold uppercase tracking-widest mr-2">Find</span>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            placeholder="Search by Name, Customer, or Opp ID..."
                                            className="border border-gray-200 rounded-lg px-4 py-2.5 text-sm w-96 focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 bg-gray-50/50 pl-10 transition-all font-medium"
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                        />
                                        <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                                    </div>
                                </div>
                            )}
                        </div>
                        <button onClick={() => fetchOpportunities()} className="flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 shadow-sm transition-all">
                            <RefreshCw size={16} /> Refresh
                        </button>
                    </div>

                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm flex-1 flex flex-col overflow-hidden">
                        <div className="flex-1 overflow-auto">
                            <OpportunitiesTable
                                opportunities={opportunities}
                                loading={loading}
                                onAssign={(opp) => { setSelectedOppId([opp.id]); setIsAssignModalOpen(true); }}
                                onApprove={(id) => openApprovalModal(id, 'APPROVE')}
                                onReject={(id) => openApprovalModal(id, 'REJECT')}
                                onView={(id, jumpToScore) => {
                                    if (jumpToScore) navigate(`/score/${id}`);
                                    else navigate(`/opportunity/${id}`);
                                }}
                                formatCurrency={formatCurrency}
                                selectedIds={selectedOppId as any}
                                onSelectionChange={setSelectedOppId as any}
                                role="PH"
                            />
                        </div>

                        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
                            <Pagination
                                currentPage={currentPage}
                                totalCount={totalCount}
                                pageSize={pageSize}
                                onPageChange={setCurrentPage}
                            />
                        </div>
                    </div>
                </div>
            </div>

            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                opportunityIds={selectedOppId}
                onAssign={(data: AssignmentData) => {
                    handleAssignToSA(selectedOppId, data.sa_owner);
                }}
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
