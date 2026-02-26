import { API_URL } from '../config';
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { UserPlus, CheckCircle, XCircle, RefreshCw, Search, BarChart3, TrendingUp, PieChart, ChevronDown, AlertCircle, PlayCircle, FileText, FileSpreadsheet, File as FileIcon } from 'lucide-react';
import { exportToCSV, exportToExcel, exportToPDF } from '../utils/exportUtils';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable, FilterState } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ApprovalModal } from '../components/ApprovalModal';
import { MultiSelect } from '../components/MultiSelect';
import { useAuth } from '../context/AuthContext';

type TabType = 'all' | 'action-required' | 'in-progress' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'all': 'All My Items',
    'action-required': 'Action Required',
    'in-progress': 'In Progress',
    'review': 'Review',
    'completed': 'Completed'
};

export function PracticeHeadDashboard() {
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
    const [selectedTabs, setSelectedTabs] = useState<string[]>(['all']);
    const [columnFilters, setColumnFilters] = useState<FilterState[]>([]);

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
        if (user?.role === 'SA') {
            navigate('/assigned-to-me');
        } else if (user?.role === 'GH' || user?.role === 'SH') {
            if (user?.role === 'SH') navigate('/sales/dashboard');
            else navigate('/management/dashboard');
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

    useEffect(() => {
        if (user?.id) fetchOpportunities();
        setSelectedOppId([]);
    }, [currentPage, pageSize, debouncedSearch, selectedTabs, columnFilters, user?.id]);

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
                    setTotalCount(data.total_count || 0);
                    if (data.counts) setTabCounts(data.counts);
                    if (data.total_value) setGlobalPipelineValue(data.total_value);
                } else {
                    setOpportunities(data);
                    setTotalCount(data.length);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    const handleAssignToSA = async (oppIds: string | string[], primarySA: string) => {
        const idsToAssign = Array.isArray(oppIds) ? oppIds : [oppIds];
        try {
            await Promise.all(idsToAssign.map(id =>
                fetch(``${API_URL}`/opportunities/${id}/assign`, {
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

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-[#fcfbf8] flex flex-col font-sans text-gray-800">
            <TopBar />

            <div className="flex flex-col flex-1 p-6">
                {/* Oracle Breadcrumb/Header */}
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl text-gray-700">Practice Dashboard</h1>
                        <span className="text-gray-400 cursor-help">ⓘ</span>
                    </div>
                    <div className="flex gap-2">
                        <div className="flex items-center gap-2 bg-white px-3 py-1 border border-gray-200 rounded text-xs">
                            <span className="text-gray-500">Pipeline:</span>
                            <span className="font-bold text-gray-800">{formatCurrency(globalPipelineValue)}</span>
                        </div>
                    </div>
                </div>

                {/* Filter Toolbar - Oracle Style */}
                <div className="bg-white border border-gray-200 p-2 mb-4 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <span className="text-gray-600 font-medium">Find</span>
                            <div className="flex bg-white border border-gray-300 rounded overflow-hidden">
                                <select className="bg-gray-50 px-1 border-r border-gray-300 outline-none">
                                    <option>Name</option>
                                </select>
                                <input
                                    type="text"
                                    className="px-2 py-0.5 outline-none w-48"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                                <button className="px-2 bg-gray-50 hover:bg-gray-100 border-l border-gray-300">
                                    <Search size={14} className="text-gray-500" />
                                </button>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 border-l border-gray-200 pl-4">
                            <MultiSelect
                                label="View List"
                                options={Object.entries(TAB_LABELS).map(([k, v]) => ({ label: v, value: k, count: tabCounts[k] }))}
                                selected={selectedTabs}
                                onChange={setSelectedTabs}
                                placeholder="All My Items"
                            />
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
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="relative">
                            <button
                                onClick={() => setIsActionsOpen(!isActionsOpen)}
                                className="px-3 py-1 bg-white border border-gray-300 rounded text-xs font-semibold hover:bg-gray-50 flex items-center gap-1 min-w-[80px]"
                            >
                                Actions <ChevronDown size={12} className={`transition-transform ${isActionsOpen ? 'rotate-180' : ''}`} />
                            </button>

                            {isActionsOpen && (
                                <div className="absolute right-0 mt-1 w-48 bg-white border border-gray-200 shadow-lg rounded z-50 py-1">
                                    <div className="px-3 py-1 text-[10px] font-bold text-gray-400 uppercase tracking-wider border-b border-gray-100">Export As</div>
                                    <button
                                        onClick={() => { exportToExcel(opportunities, 'opportunities_export'); setIsActionsOpen(false); }}
                                        className="w-full text-left px-4 py-2 text-xs hover:bg-gray-50 flex items-center gap-2"
                                    >
                                        <FileSpreadsheet size={14} className="text-green-600" /> Excel (.xlsx)
                                    </button>
                                    <button
                                        onClick={() => { exportToCSV(opportunities, 'opportunities_export'); setIsActionsOpen(false); }}
                                        className="w-full text-left px-4 py-2 text-xs hover:bg-gray-50 flex items-center gap-2"
                                    >
                                        <FileIcon size={14} className="text-blue-600" /> CSV (.csv)
                                    </button>
                                    <button
                                        onClick={() => { exportToPDF(opportunities, 'opportunities_export'); setIsActionsOpen(false); }}
                                        className="w-full text-left px-4 py-2 text-xs hover:bg-gray-50 flex items-center gap-2"
                                    >
                                        <FileText size={14} className="text-red-600" /> PDF (.pdf)
                                    </button>
                                </div>
                            )}
                        </div>
                        <button className="px-3 py-1 bg-white border border-gray-300 rounded text-xs font-semibold hover:bg-gray-50 text-blue-700">
                            Advanced Search
                        </button>
                    </div>
                </div>

                {/* Selected Status Bar */}
                {selectedOppId.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 px-4 py-2 mb-4 flex items-center justify-between animate-in fade-in slide-in-from-top-1">
                        <div className="flex items-center gap-3">
                            <span className="text-xs font-bold text-blue-800">{selectedOppId.length} Selected</span>
                            <div className="flex gap-2">
                                <button onClick={() => setIsAssignModalOpen(true)} className="oracle-btn !bg-white">Assign SA</button>
                                {selectedTabs.includes('review') && (
                                    <>
                                        <button onClick={() => openApprovalModal(selectedOppId, 'APPROVE')} className="oracle-btn !bg-green-600 !text-white !border-green-700">Approve</button>
                                        <button onClick={() => openApprovalModal(selectedOppId, 'REJECT')} className="oracle-btn !bg-red-600 !text-white !border-red-700">Reject</button>
                                    </>
                                )}
                            </div>
                        </div>
                        <button onClick={() => setSelectedOppId([])} className="text-xs text-blue-700 hover:underline">Clear Selection</button>
                    </div>
                )}

                {/* Metric Summary Cards - Simplified */}
                <div className="grid grid-cols-4 gap-4 mb-4">
                    {[
                        { label: 'Action Required', count: tabCounts['action-required'] || 0, tab: 'action-required', color: 'border-red-400' },
                        { label: 'In Progress', count: tabCounts['in-progress'] || 0, tab: 'in-progress', color: 'border-blue-400' },
                        { label: 'Review', count: tabCounts['review'] || 0, tab: 'review', color: 'border-purple-400' },
                        { label: 'Completed', count: tabCounts['completed'] || 0, tab: 'completed', color: 'border-green-400' }
                    ].map(m => (
                        <div
                            key={m.label}
                            onClick={() => navigate(`/practice-head/${m.tab}`)}
                            className={`bg-white p-3 border-t-2 ${m.color} border-x border-b border-gray-200 shadow-sm cursor-pointer hover:bg-gray-50 transition-colors`}
                        >
                            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-tight mb-1">{m.label}</div>
                            <div className="text-xl font-bold text-gray-700">{m.count}</div>
                        </div>
                    ))}
                </div>

                {/* Table Area */}
                <div className="flex-1 min-h-0 flex flex-col">
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
                            selectedIds={selectedOppId}
                            onSelectionChange={setSelectedOppId}
                            role="PH"
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

                    <div className="bg-white border border-gray-200 border-t-0 p-3">
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
                title="Assign Solution Architect"
                targetRole="SA"
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
