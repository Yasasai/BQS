import { API_URL } from '../config';
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, RefreshCw, Search, TrendingUp, BarChart3, PieChart, AlertCircle, PlayCircle, FileText, CheckCircle, UserPlus, XCircle, FileSpreadsheet, File as FileIcon } from 'lucide-react';
import { exportToCSV, exportToExcel, exportToPDF } from '../utils/exportUtils';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable, FilterState } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ApprovalModal } from '../components/ApprovalModal';
import { MultiSelect } from '../components/MultiSelect';

type TabType = 'all' | 'action-required' | 'in-progress' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'all': 'All My Items',
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
    const [columnFilters, setColumnFilters] = useState<FilterState[]>([]);

    const [selectedTabs, setSelectedTabs] = useState<string[]>(['all']);

    // Metadata for filters
    const [allRegions, setAllRegions] = useState<string[]>([]);
    const [allPractices, setAllPractices] = useState<string[]>([]);
    const [allStages, setAllStages] = useState<string[]>([]);
    const [allStatuses, setAllStatuses] = useState<string[]>([]);
    const [isActionsOpen, setIsActionsOpen] = useState(false);

    useEffect(() => {
        const endpoints = ['regions', 'practices', 'stages', 'statuses'];
        endpoints.forEach(end => {
            fetch(``${API_URL}`/opportunities/metadata/${end}`)
                .then(res => res.json())
                .then(data => {
                    if (end === 'regions') setAllRegions(data);
                    if (end === 'practices') setAllPractices(data);
                    if (end === 'stages') setAllStages(data);
                    if (end === 'statuses') setAllStatuses(data);
                })
                .catch(err => console.error(`Failed to fetch ${end}`, err));
        });
    }, []);

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<string[]>([]);

    // Role-based Access Control
    useEffect(() => {
        if (user?.role !== 'SH' && user?.role !== 'GH') {
            if (user?.role === 'PH') navigate('/practice-head/dashboard');
            if (user?.role === 'SA' || user?.role === 'SP') navigate('/assigned-to-me');
        }
    }, [user, navigate]);

    // Sync URL with Tab
    useEffect(() => {
        const path = location.pathname;
        if (path.includes('action-required')) setSelectedTabs(['action-required']);
        else if (path.includes('in-progress')) setSelectedTabs(['in-progress']);
        else if (path.includes('review')) setSelectedTabs(['review']);
        else if (path.includes('completed')) setSelectedTabs(['completed']);
        else if (path.includes('all')) setSelectedTabs(['all']);
        else setSelectedTabs(['action-required']);
    }, [location.pathname]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
            setCurrentPage(1);
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    // Fetch on changes
    useEffect(() => {
        if (user?.id) fetchOpportunities();
        setSelectedOppId([]);
    }, [currentPage, pageSize, debouncedSearch, selectedTabs, user?.id, columnFilters]);

    const fetchOpportunities = () => {
        setLoading(true);

        const params = new URLSearchParams({
            page: currentPage.toString(),
            limit: pageSize.toString(),
            tab: selectedTabs.join(','),
            user_id: user?.id || '',
            role: user?.role || ''
        });
        if (debouncedSearch) params.append('search', debouncedSearch);
        if (columnFilters.length > 0) params.append('filters', JSON.stringify(columnFilters));

        fetch(``${API_URL}`/opportunities/?${params}`)
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

    const [assignTargetRole, setAssignTargetRole] = useState<'SP' | 'PH'>('SP');

    const handleAssign = async (oppIds: string | string[], userId: string) => {
        const idsToAssign = Array.isArray(oppIds) ? oppIds : [oppIds];
        try {
            await Promise.all(idsToAssign.map(id =>
                fetch(``${API_URL}`/opportunities/${id}/assign`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        role: assignTargetRole,
                        user_id: userId,
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
                fetch(``${API_URL}`/opportunities/${id}/approve`, {
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
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1 p-8">
                {/* Header Section */}
                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Sales Head Dashboard</h1>
                        <div className="flex items-center gap-2 text-gray-500 font-medium">
                            <p>Team Performance & Pipeline Management</p>
                        </div>
                    </div>
                    <div className="bg-white px-6 py-4 rounded-2xl border border-gray-200 shadow-sm flex items-center gap-6">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Pipeline Value</span>
                            <span className="text-2xl font-black text-blue-600">{formatCurrency(globalPipelineValue)}</span>
                        </div>
                        <div className="h-10 w-[1px] bg-gray-100" />
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Total Assigned</span>
                            <span className="text-2xl font-black text-gray-900">{tabCounts['all'] || 0}</span>
                        </div>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sales/action-required')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-red-100 text-red-600 rounded-lg group-hover:scale-110 transition-transform"><AlertCircle size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Action Required</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['action-required'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sales/in-progress')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-blue-100 text-blue-600 rounded-lg group-hover:scale-110 transition-transform"><PlayCircle size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">In Progress</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['in-progress'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sales/review')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-amber-100 text-amber-600 rounded-lg group-hover:scale-110 transition-transform"><FileText size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Review</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{tabCounts['review'] || 0}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sales/completed')}>
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
                                onClick={() => setSelectedTabs([t])}
                                className={`py-6 text-xs font-black uppercase tracking-[0.2em] relative transition-all ${selectedTabs.includes(t) ? 'text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                {TAB_LABELS[t]} ({tabCounts[t] || 0})
                                {selectedTabs.includes(t) && <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-600 rounded-t-full shadow-[0_-2px_10px_rgba(37,99,235,0.3)]" />}
                            </button>
                        ))}
                    </div>

                    {/* Toolbar */}
                    <div className="px-8 py-4 bg-gray-50/50 border-b border-gray-100 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            {/* Search */}
                            <div className="relative group">
                                <input
                                    type="text"
                                    placeholder="SEARCH OPPORTUNITIES..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-12 pr-6 py-3 bg-white border border-gray-200 rounded-2xl text-xs font-bold tracking-widest focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none w-96 transition-all group-hover:shadow-md"
                                />
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-blue-500 transition-colors" size={18} />
                            </div>

                            <div className="flex items-center gap-2 border-l border-gray-200 pl-4">
                                <MultiSelect
                                    label="Region"
                                    options={allRegions.map(r => ({ label: r.toUpperCase(), value: r }))}
                                    selected={columnFilters.find(f => f.id === 'geo')?.value || []}
                                    onChange={(vals) => {
                                        setColumnFilters(prev => {
                                            const next = prev.filter(f => f.id !== 'geo');
                                            if (vals.length > 0) next.push({ id: 'geo', value: vals });
                                            return next;
                                        });
                                    }}
                                    placeholder="All Regions"
                                />
                            </div>

                            <div className="flex items-center gap-2 border-l border-gray-200 pl-4">
                                <MultiSelect
                                    label="Practice"
                                    options={allPractices.map(p => ({ label: p.toUpperCase(), value: p }))}
                                    selected={columnFilters.find(f => f.id === 'practice')?.value || []}
                                    onChange={(vals) => {
                                        setColumnFilters(prev => {
                                            const next = prev.filter(f => f.id !== 'practice');
                                            if (vals.length > 0) next.push({ id: 'practice', value: vals });
                                            return next;
                                        });
                                    }}
                                    placeholder="All Practices"
                                />
                            </div>

                            {/* Batch Actions */}
                            {selectedOppId.length > 0 && (
                                <div className="flex items-center gap-3 animate-fade-in">
                                    <span className="text-xs font-bold text-blue-900 bg-blue-100 px-3 py-1.5 rounded-lg">{selectedOppId.length} selected</span>
                                    <button
                                        onClick={() => setSelectedOppId([])}
                                        className="text-[10px] font-bold text-gray-500 hover:text-gray-700 uppercase tracking-wider"
                                    >
                                        Clear
                                    </button>
                                    <div className="h-4 w-[1px] bg-gray-300 mx-2" />
                                    <button
                                        onClick={() => setIsAssignModalOpen(true)}
                                        className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 shadow-sm transition-all uppercase tracking-wider"
                                    >
                                        <UserPlus size={14} /> Assign SP
                                    </button>

                                    {selectedTabs.includes('review') && (
                                        <>
                                            <button
                                                onClick={() => openApprovalModal(selectedOppId, 'APPROVE')}
                                                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-white bg-green-600 rounded-xl hover:bg-green-700 shadow-sm transition-all uppercase tracking-wider"
                                            >
                                                <CheckCircle size={14} /> Approve
                                            </button>
                                            <button
                                                onClick={() => openApprovalModal(selectedOppId, 'REJECT')}
                                                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-white bg-red-600 rounded-xl hover:bg-red-700 shadow-sm transition-all uppercase tracking-wider"
                                            >
                                                <XCircle size={14} /> Reject
                                            </button>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <button
                                    onClick={() => setIsActionsOpen(!isActionsOpen)}
                                    className="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-xs font-bold uppercase tracking-wider hover:bg-gray-50 flex items-center gap-2 shadow-sm transition-all"
                                >
                                    Actions <ChevronDown size={14} className={`transition-transform ${isActionsOpen ? 'rotate-180' : ''}`} />
                                </button>

                                {isActionsOpen && (
                                    <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-100 shadow-2xl rounded-2xl z-50 py-2 animate-in fade-in zoom-in duration-200">
                                        <div className="px-4 py-2 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-50 mb-1">Export Data</div>
                                        <button
                                            onClick={() => { exportToExcel(opportunities, 'sales_opportunities'); setIsActionsOpen(false); }}
                                            className="w-full text-left px-4 py-3 text-xs font-bold text-gray-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-green-50 text-green-600 rounded-lg"><FileSpreadsheet size={16} /></div>
                                            Excel (.xlsx)
                                        </button>
                                        <button
                                            onClick={() => { exportToCSV(opportunities, 'sales_opportunities'); setIsActionsOpen(false); }}
                                            className="w-full text-left px-4 py-3 text-xs font-bold text-gray-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg"><FileIcon size={16} /></div>
                                            CSV (.csv)
                                        </button>
                                        <button
                                            onClick={() => { exportToPDF(opportunities, 'sales_opportunities'); setIsActionsOpen(false); }}
                                            className="w-full text-left px-4 py-3 text-xs font-bold text-gray-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-red-50 text-red-600 rounded-lg"><FileText size={16} /></div>
                                            PDF (.pdf)
                                        </button>
                                    </div>
                                )}
                            </div>
                            <button onClick={() => fetchOpportunities()} className="p-3 bg-white border border-gray-200 rounded-2xl hover:bg-gray-50 transition-all hover:rotate-180 duration-500 shadow-sm">
                                <RefreshCw size={20} className="text-gray-400" />
                            </button>
                        </div>
                    </div>

                    {/* Table */}
                    <div className="flex-1 overflow-auto px-8 py-4">
                        <OpportunitiesTable
                            opportunities={opportunities}
                            loading={loading}
                            onAssign={(opp, type) => {
                                setSelectedOppId([opp.id]);
                                setAssignTargetRole((type as any) || 'SP');
                                setIsAssignModalOpen(true);
                            }}
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
                            filters={columnFilters}
                            onFilterChange={setColumnFilters}
                            metadata={{
                                regions: allRegions,
                                practices: allPractices,
                                stages: allStages,
                                statuses: allStatuses
                            }}
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

            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                opportunityIds={selectedOppId}
                targetRole={assignTargetRole}
                title={assignTargetRole === 'SP' ? "Assign Sales Representative" : "Assign Practice Head"}
                onAssign={(data: AssignmentData) => { handleAssign(selectedOppId, data.sa_owner); }}
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
