import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { RefreshCw, Search, BarChart3, TrendingUp, CheckCircle, PieChart, ChevronDown, FileSpreadsheet, FileText, File as FileIcon } from 'lucide-react';
import { exportToCSV, exportToExcel, exportToPDF } from '../utils/exportUtils';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { MultiSelect } from '../components/MultiSelect';
import { useAuth } from '../context/AuthContext';

type TabType = 'all' | 'needs-action' | 'in-progress' | 'submitted';

const TAB_LABELS: Record<string, string> = {
    'all': 'All My Tasks',
    'needs-action': 'Needs Action',
    'in-progress': 'In Progress',
    'submitted': 'Submitted'
};

export function SolutionArchitectDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [globalPipelineValue, setGlobalPipelineValue] = useState(0);

    // Pagination & Search State
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(50);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [selectedTabs, setSelectedTabs] = useState<string[]>(['needs-action']);

    const [columnFilters, setColumnFilters] = useState<any[]>([]);

    // Metadata for filters
    const [allRegions, setAllRegions] = useState<string[]>([]);
    const [allPractices, setAllPractices] = useState<string[]>([]);
    const [allStages, setAllStages] = useState<string[]>([]);
    const [allStatuses, setAllStatuses] = useState<string[]>([]);
    const [isActionsOpen, setIsActionsOpen] = useState(false);

    useEffect(() => {
        const endpoints = ['regions', 'practices', 'stages', 'statuses'];
        endpoints.forEach(end => {
            fetch(`http://localhost:8000/api/opportunities/metadata/${end}`)
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



    // Sync URL with Tab
    useEffect(() => {
        const path = window.location.pathname;
        if (path.includes('assigned')) setSelectedTabs(['needs-action']);
        else if (path.includes('start')) setSelectedTabs(['in-progress']);
        else if (path.includes('submitted')) setSelectedTabs(['submitted']);
        else if (path.includes('all')) setSelectedTabs(['all']);
        else setSelectedTabs(['needs-action']);
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
        if (user?.id) fetchOpportunities();
    }, [currentPage, pageSize, debouncedSearch, selectedTabs, columnFilters, user?.id]);

    const fetchOpportunities = () => {
        setLoading(true);
        // SA fetches all assigned to them using role=SA
        const params = new URLSearchParams({
            page: currentPage.toString(),
            limit: pageSize.toString(),
            user_id: user?.id || '',
            role: user?.role || '',
            tab: selectedTabs.map(t => t === 'needs-action' ? 'action-required' : t).join(',')
        });
        if (debouncedSearch) params.append('search', debouncedSearch);
        if (columnFilters.length > 0) params.append('filters', JSON.stringify(columnFilters));

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
                    if (data.total_value) setGlobalPipelineValue(data.total_value);
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

    const [tabCounts, setTabCounts] = useState<Record<string, number>>({});
    const counts = {
        'needs-action': tabCounts['needs-action'] || tabCounts['action-required'] || 0,
        'in-progress': tabCounts['in-progress'] || 0,
        'submitted': tabCounts['submitted'] || 0,
        'all': tabCounts['all'] || 0
    };

    const handleStartAssessment = async (oppId: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/start-assessment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sa_name: user?.name })
            });

            if (!response.ok) throw new Error('Failed to start assessment');

            navigate(`/score/${oppId}`);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to start assessment');
        }
    };

    const handleContinueAssessment = (oppId: string) => {
        navigate(`/score/${oppId}`);
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1 p-8">
                {/* Header Section */}
                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                            {user?.role === 'SP' ? 'Sales Representative Dashboard' : 'Solution Architect Dashboard'}
                        </h1>
                        <div className="flex items-center gap-2 text-gray-500 font-medium">
                            <p>{user?.role === 'SP' ? 'Opportunity Assessment & Commercial Review' : 'Assessment Execution & Technical Review'}</p>
                        </div>
                    </div>
                    <div className="bg-white px-6 py-4 rounded-2xl border border-gray-200 shadow-sm flex items-center gap-6">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Pipeline Value</span>
                            <span className="text-2xl font-black text-blue-600">{formatCurrency(globalPipelineValue)}</span>
                        </div>
                        <div className="h-10 w-[1px] bg-gray-100" />
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Assigned</span>
                            <span className="text-2xl font-black text-gray-900">{totalCount}</span>
                        </div>
                    </div>
                </div>

                {/* Metrics Bar */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sa/assigned')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-blue-100 text-blue-600 rounded-lg group-hover:scale-110 transition-transform"><BarChart3 size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">New Assignments</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{counts['needs-action']}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sa/start')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg group-hover:scale-110 transition-transform"><TrendingUp size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">In Progress</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{counts['in-progress']}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sa/submitted')}>
                        <div className="flex items-center gap-4 mb-3">
                            <div className="p-2 bg-orange-100 text-orange-600 rounded-lg group-hover:scale-110 transition-transform"><PieChart size={20} /></div>
                            <span className="text-sm font-bold text-gray-400 uppercase tracking-widest">Submitted</span>
                        </div>
                        <div className="text-3xl font-black text-gray-900">{counts['submitted']}</div>
                    </div>
                    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={() => navigate('/sa/submitted')}>
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

                            <div className="relative group">
                                <input
                                    type="text"
                                    placeholder="SEARCH MY ASSIGNMENTS..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-12 pr-6 py-3 bg-white border border-gray-200 rounded-2xl text-xs font-bold tracking-widest focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none w-96 transition-all group-hover:shadow-md"
                                />
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-blue-500 transition-colors" size={18} />
                            </div>
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
                                            onClick={() => { exportToExcel(opportunities, 'sa_opportunities'); setIsActionsOpen(false); }}
                                            className="w-full text-left px-4 py-3 text-xs font-bold text-gray-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-green-50 text-green-600 rounded-lg"><FileSpreadsheet size={16} /></div>
                                            Excel (.xlsx)
                                        </button>
                                        <button
                                            onClick={() => { exportToCSV(opportunities, 'sa_opportunities'); setIsActionsOpen(false); }}
                                            className="w-full text-left px-4 py-3 text-xs font-bold text-gray-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 transition-colors"
                                        >
                                            <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg"><FileIcon size={16} /></div>
                                            CSV (.csv)
                                        </button>
                                        <button
                                            onClick={() => { exportToPDF(opportunities, 'sa_opportunities'); setIsActionsOpen(false); }}
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

                    {/* Table Wrapper */}
                    <div className="flex-1 overflow-auto px-8 py-4">
                        <OpportunitiesTable
                            opportunities={opportunities}
                            loading={loading}
                            onView={(id) => navigate(`/opportunity/${id}`)}
                            onStartAssessment={handleStartAssessment}
                            onContinueAssessment={handleContinueAssessment}
                            onAssign={() => { }} // SA doesn't assign
                            onApprove={() => { }} // SA doesn't approve in this view
                            onReject={() => { }}
                            formatCurrency={formatCurrency}
                            selectedIds={[]}
                            onSelectionChange={() => { }}
                            role={user?.role as any}
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

        </div>
    );
}
