import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { CheckCircle, XCircle, Search, RefreshCw, BarChart3, TrendingUp, PieChart } from 'lucide-react';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ApprovalModal } from '../components/ApprovalModal';
import { useAuth } from '../context/AuthContext';

type TabType = 'unassigned' | 'missing-ph' | 'missing-sh' | 'in-progress' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'unassigned': 'Unassigned',
    'missing-ph': 'Missing Practice Head',
    'missing-sh': 'Missing Sales Head',
    'in-progress': 'In Progress',
    'review': 'Under Review',
    'completed': 'Completed'
};

export function ManagementDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
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
    const [activeTab, setActiveTab] = useState<TabType>('unassigned');

    const [selectedOppId, setSelectedOppId] = useState<(string | number)[]>([]);

    // Role-based Access Control
    useEffect(() => {
        if (user?.role === 'SA') navigate('/assigned-to-me');
        else if (user?.role === 'PH') navigate('/practice-head/dashboard');
    }, [user, navigate]);

    // Sync URL with Tab
    useEffect(() => {
        const path = window.location.pathname;
        const matchedTab = (Object.keys(TAB_LABELS) as TabType[]).find(t => path.includes(t));
        if (matchedTab) setActiveTab(matchedTab);
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
            .then(res => res.json())
            .then(data => {
                if (data.items && Array.isArray(data.items)) {
                    setOpportunities(data.items);
                    setTotalCount(data.total_count || 0);
                    if (data.counts) setTabCounts(data.counts);
                    if (data.total_value) setGlobalPipelineValue(data.total_value);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    // --- Approval Modal Logic ---
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
                        role: user?.role,
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
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1 p-8">
                {/* Header Section */}
                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Global Pipeline Governance</h1>
                        <p className="text-gray-500 font-medium">Monitoring {totalCount} Opportunities Across All Regions</p>
                    </div>
                    <div className="bg-white px-6 py-4 rounded-2xl border border-gray-200 shadow-sm flex items-center gap-6">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Total Value</span>
                            <span className="text-2xl font-black text-blue-600">{formatCurrency(globalPipelineValue)}</span>
                        </div>
                        <div className="h-10 w-[1px] bg-gray-100" />
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Active Items</span>
                            <span className="text-2xl font-black text-gray-900">{totalCount}</span>
                        </div>
                    </div>
                </div>

                {/* Metrics Bar */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group">
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-orange-100 text-orange-600 rounded-lg group-hover:scale-110 transition-transform"><BarChart3 size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Unassigned</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['unassigned'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group">
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-blue-100 text-blue-600 rounded-lg group-hover:scale-110 transition-transform"><TrendingUp size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">In Progress</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['in-progress'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group">
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-purple-100 text-purple-600 rounded-lg group-hover:scale-110 transition-transform"><PieChart size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Under Review</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['review'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group">
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-green-100 text-green-600 rounded-lg group-hover:scale-110 transition-transform"><CheckCircle size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Completed</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['completed'] || 0}</div>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="bg-white rounded-3xl shadow-xl border border-gray-200 overflow-hidden flex flex-col flex-1">
                    {/* Tabs */}
                    <div className="flex items-center gap-8 px-8 border-b border-gray-100">
                        {(Object.keys(TAB_LABELS) as TabType[]).map(t => (
                            <button
                                key={t}
                                onClick={() => navigate(`/management/${t}`)}
                                className={`py-6 text-xs font-black uppercase tracking-[0.2em] relative transition-all ${activeTab === t ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                {TAB_LABELS[t]} ({tabCounts[t] || 0})
                                {activeTab === t && <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-600 rounded-t-full shadow-[0_-2px_10px_rgba(37,99,235,0.3)]" />}
                            </button>
                        ))}
                    </div>

                    {/* Toolbar */}
                    <div className="px-8 py-4 bg-gray-50/50 border-b border-gray-100 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            {selectedOppId.length > 0 ? (
                                <div className="flex items-center gap-3 animate-in fade-in slide-in-from-left-4">
                                    <div className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-black shadow-lg">
                                        {selectedOppId.length} SELECTED
                                    </div>
                                    <button onClick={() => setSelectedOppId([])} className="text-xs font-bold text-gray-400 hover:text-gray-600 uppercase tracking-widest">Clear</button>
                                    <div className="h-6 w-[1px] bg-gray-200 mx-2" />
                                    {activeTab === 'review' && (
                                        <div className="flex gap-2">
                                            <button onClick={() => openApprovalModal(selectedOppId, 'APPROVE')} className="px-6 py-2 bg-green-600 text-white text-xs font-black rounded-xl shadow-md hover:bg-green-700 transition-all uppercase tracking-widest">Approve</button>
                                            <button onClick={() => openApprovalModal(selectedOppId, 'REJECT')} className="px-6 py-2 bg-red-600 text-white text-xs font-black rounded-xl shadow-md hover:bg-red-700 transition-all uppercase tracking-widest">Reject</button>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="relative group">
                                    <input
                                        type="text"
                                        placeholder="SEARCH GLOBAL PIPELINE..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="pl-12 pr-6 py-3 bg-white border border-gray-200 rounded-2xl text-xs font-bold tracking-widest focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none w-96 transition-all group-hover:shadow-md"
                                    />
                                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-blue-500 transition-colors" size={18} />
                                </div>
                            )}
                        </div>
                        <button onClick={() => fetchOpportunities()} className="p-3 bg-white border border-gray-200 rounded-2xl hover:bg-gray-50 transition-all hover:rotate-180 duration-500 shadow-sm">
                            <RefreshCw size={20} className="text-gray-400" />
                        </button>
                    </div>

                    {/* Table Wrapper */}
                    <div className="flex-1 overflow-auto px-8 py-4">
                        <OpportunitiesTable
                            opportunities={opportunities}
                            loading={loading}
                            onView={(id, jumpToScore) => {
                                if (jumpToScore) navigate(`/score/${id}`);
                                else navigate(`/opportunity/${id}`);
                            }}
                            onApprove={(id) => openApprovalModal(id, 'APPROVE')}
                            onReject={(id) => openApprovalModal(id, 'REJECT')}
                            formatCurrency={formatCurrency}
                            selectedIds={selectedOppId as any}
                            onSelectionChange={setSelectedOppId as any}
                            role={user?.role || 'GH'}
                        />
                    </div>

                    {/* Pagination */}
                    <div className="px-8 py-6 bg-gray-50/50 border-t border-gray-100">
                        <Pagination
                            currentPage={currentPage}
                            totalCount={totalCount}
                            pageSize={pageSize}
                            onPageChange={setCurrentPage}
                        />
                    </div>
                </div>
            </div>

            <ApprovalModal
                isOpen={isApprovalModalOpen}
                onClose={() => setIsApprovalModalOpen(false)}
                onConfirm={handleModalConfirm}
                type={approvalAction || 'APPROVE'}
            />
        </div>
    );
}
