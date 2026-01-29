import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';

type TabType = 'unassigned' | 'under-assessment' | 'pending-review' | 'all';

export function PracticeHeadDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('all');
    const [viewMode, setViewMode] = useState('All Opportunities');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<number[]>([]);

    // Action menu state
    const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);

    useEffect(() => {
        fetchOpportunities();
    }, []);

    const fetchOpportunities = () => {
        setLoading(true);
        fetch('http://localhost:8000/api/opportunities')
            .then(res => res.json())
            .then(data => {
                setOpportunities(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    // --- Metrics Calculations ---
    const totalOpps = opportunities.length;
    const pipelineValue = opportunities.reduce((sum, o) => sum + (o.deal_value || 0), 0);
    const avgWinProb = totalOpps > 0 ? Math.round(opportunities.reduce((sum, o) => sum + (o.win_probability || 0), 0) / totalOpps) : 0;
    const awaitingReviewCount = opportunities.filter(o => o.workflow_status === 'SUBMITTED_FOR_REVIEW').length;

    // Distribution counts
    const statusCounts = {
        NEW: opportunities.filter(o => !o.workflow_status || o.workflow_status === 'NEW').length,
        ASSIGNED: opportunities.filter(o => o.workflow_status === 'ASSIGNED_TO_SA').length,
        ASSESSMENT: opportunities.filter(o => o.workflow_status === 'UNDER_ASSESSMENT').length,
        REVIEW: opportunities.filter(o => o.workflow_status === 'SUBMITTED_FOR_REVIEW').length,
        COMPLETED: opportunities.filter(o => ['APPROVED', 'COMPLETED', 'WON', 'LOST'].includes(o.workflow_status || '')).length
    };

    // --- Filtering ---
    const getFilteredOpportunities = () => {
        if (viewMode === 'My Team') {
            // Placeholder logic for team filtering
            return opportunities;
        }
        return opportunities;
    };
    const filteredOpportunities = getFilteredOpportunities();


    const handleAssignToSA = async (oppId: number, primarySA: string, secondarySA?: string) => {
        // ... (Keep existing logic or stub)
        console.log(`Assigning ${oppId} to ${primarySA}`);
        setIsAssignModalOpen(false);
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-[#FDF3E1] flex flex-col font-sans text-[#333333]">
            <TopBar title="Executive Dashboard" />

            <div className="flex-1 px-8 py-6 max-w-[1600px] mx-auto w-full">

                {/* Header Section */}
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-2">
                        <h1 className="text-2xl font-normal text-[#333333]">Executive Analytics</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-400 font-bold cursor-help">?</div>
                    </div>
                    <div className="flex items-center gap-2 bg-green-50 border border-green-200 px-3 py-1 rounded text-xs font-bold text-green-700">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        ORACLE CRM LINK: ACTIVE
                    </div>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    {/* Card 1: TOTAL PIPELINE */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">TOTAL OPPORTUNITIES</div>
                        <div className="text-4xl font-normal text-[#0073BB] mb-2">{totalOpps}</div>
                        <div className="text-[12px] text-[#666666]">Active engagements</div>
                    </div>
                    {/* Card 2: PIPELINE VALUE */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">PIPELINE VALUE</div>
                        <div className="text-4xl font-normal text-[#217346] mb-2">${(pipelineValue / 1000000).toFixed(1)}M</div>
                        <div className="text-[12px] text-[#666666]">{formatCurrency(pipelineValue)}</div>
                    </div>
                    {/* Card 3: AVG WIN PROB */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">AVG WIN PROBABILITY</div>
                        <div className="text-4xl font-normal text-[#E27D12] mb-2">{avgWinProb}%</div>
                        <div className="text-[12px] text-[#666666]">Qualified pipeline average</div>
                    </div>
                    {/* Card 4: ACTION REQUIRED */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">AWAITING REVIEW</div>
                        <div className="text-4xl font-normal text-[#A80000] mb-2">{awaitingReviewCount}</div>
                        <div className="text-[12px] text-[#666666]">Critical approvals pending</div>
                    </div>
                </div>

                {/* Pipeline Distribution Section */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
                    <div className="flex justify-between items-center mb-6">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider">PIPELINE DISTRIBUTION BY WORKFLOW STATUS</div>
                        <div className="flex gap-4">
                            <div className="flex items-center gap-2 text-[11px] font-bold text-[#666666]">
                                <RefreshCw size={12} className="cursor-pointer hover:rotate-180 transition-transform duration-500" onClick={fetchOpportunities} />
                                SYNCED 2M AGO
                            </div>
                        </div>
                    </div>

                    {/* Tiered Progress Bar */}
                    <div className="flex h-3 w-full rounded-full overflow-hidden bg-[#F2F2F2] mb-6">
                        <div style={{ width: `${(statusCounts.NEW / totalOpps) * 100}%` }} className="bg-[#94A3B8] transition-all duration-1000"></div>
                        <div style={{ width: `${(statusCounts.ASSIGNED / totalOpps) * 100}%` }} className="bg-[#0073BB] transition-all duration-1000"></div>
                        <div style={{ width: `${(statusCounts.ASSESSMENT / totalOpps) * 100}%` }} className="bg-[#E27D12] transition-all duration-1000"></div>
                        <div style={{ width: `${(statusCounts.REVIEW / totalOpps) * 100}%` }} className="bg-[#A80000] transition-all duration-1000"></div>
                        <div style={{ width: `${(statusCounts.COMPLETED / totalOpps) * 100}%` }} className="bg-[#217346] transition-all duration-1000"></div>
                    </div>

                    <div className="flex flex-wrap gap-8 text-[11px] text-[#666666] font-bold uppercase tracking-tight">
                        <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-sm bg-[#94A3B8]"></div> NEW ({statusCounts.NEW})</div>
                        <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-sm bg-[#0073BB]"></div> ASSIGNED ({statusCounts.ASSIGNED})</div>
                        <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-sm bg-[#E27D12]"></div> ASSESSMENT ({statusCounts.ASSESSMENT})</div>
                        <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-sm bg-[#A80000]"></div> REVIEW ({statusCounts.REVIEW})</div>
                        <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 rounded-sm bg-[#217346]"></div> COMPLETED ({statusCounts.COMPLETED})</div>
                    </div>
                </div>

                {/* Optimized Toolbar */}
                <div className="flex items-center justify-between bg-white p-4 rounded-t-lg border border-gray-200 border-b-0 shadow-sm">
                    <div className="flex items-center gap-6">
                        <button className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                            <Filter size={18} className="text-[#666666]" /> Filters
                        </button>

                        <div className="flex items-center gap-2">
                            <span className="text-sm font-normal text-[#666666]">View</span>
                            <div className="relative">
                                <button className="flex items-center gap-8 px-4 py-2 text-sm font-normal text-[#333333] border border-gray-300 rounded bg-white hover:bg-gray-50">
                                    {viewMode} <ChevronDown size={14} className="text-[#666666]" />
                                </button>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 bg-[#F9FAFB] border border-gray-300 rounded px-4 py-2 w-72">
                            <Search size={18} className="text-[#666666]" />
                            <input
                                type="text"
                                placeholder="Search by name, customer..."
                                className="bg-transparent border-none w-full text-sm focus:outline-none placeholder:text-gray-400"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button onClick={fetchOpportunities} className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50 flex-shrink-0">
                            <RefreshCw size={18} className="text-[#666666]" /> Refresh
                        </button>
                        <button className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50 flex-shrink-0">
                            <Download size={18} className="text-[#666666]" /> Export
                        </button>
                    </div>
                </div>

                {/* Data Table */}
                <div className="bg-white border border-gray-200 rounded-b-lg overflow-x-auto shadow-sm mb-12">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-[#F9FAFB]">
                            <tr>
                                <th className="px-6 py-4 text-left w-10">
                                    <input type="checkbox" className="rounded text-[#0073BB] focus:ring-[#0073BB] border-gray-300" />
                                </th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Opp Number</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Opportunity Name</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Customer</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Assigned SA</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Practice</th>
                                <th className="px-4 py-4 text-right text-[11px] font-bold text-[#666666] uppercase tracking-wider">Deal Value</th>
                                <th className="px-4 py-4 text-right text-[11px] font-bold text-[#666666] uppercase tracking-wider">Win (%)</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Workflow Status</th>
                                <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Exp Close</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-100">
                            {loading ? (
                                <tr><td colSpan={10} className="px-6 py-24 text-center">
                                    <div className="flex flex-col items-center gap-4">
                                        <RefreshCw size={32} className="text-[#0073BB] animate-spin" />
                                        <span className="text-sm font-bold text-[#666666] uppercase tracking-widest">Hydrating Pipeline Data...</span>
                                    </div>
                                </td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={10} className="px-6 py-24 text-center text-gray-400 font-medium">No results matched your current filters.</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => (
                                    <tr
                                        key={opp.id}
                                        className="hover:bg-blue-50/40 transition-colors group cursor-pointer text-[13px] text-[#333333]"
                                        onClick={() => navigate(`/opportunity/${opp.id}`)}
                                    >
                                        <td className="px-6 py-4" onClick={e => e.stopPropagation()}>
                                            <input type="checkbox" className="rounded text-[#0073BB] focus:ring-[#0073BB] border-gray-300" />
                                        </td>
                                        <td className="px-4 py-4 text-[#666666] font-medium">
                                            {opp.remote_id}
                                        </td>
                                        <td className="px-4 py-4 text-[#0073BB] font-semibold hover:underline decoration-1 underline-offset-4">
                                            {opp.name}
                                        </td>
                                        <td className="px-4 py-4 text-[#333333]">
                                            {opp.customer}
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="flex items-center gap-2">
                                                <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-[10px] text-gray-500 font-bold border border-gray-200">
                                                    {opp.assigned_sa?.charAt(0) || '?'}
                                                </div>
                                                <span className="text-[#666666]">{opp.assigned_sa || 'Unassigned'}</span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.practice || '-'}
                                        </td>
                                        <td className="px-4 py-4 text-right font-semibold text-[#217346]">
                                            {formatCurrency(opp.deal_value)}
                                        </td>
                                        <td className="px-4 py-4 text-right pr-8">
                                            <div className="inline-block px-2 py-0.5 rounded font-bold text-[11px] bg-[#FFE57F] text-[#333333]">
                                                {opp.win_probability || 0}%
                                            </div>
                                        </td>
                                        <td className="px-4 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${opp.workflow_status === 'SUBMITTED_FOR_REVIEW' ? 'bg-[#A80000] text-white' :
                                                    opp.workflow_status === 'COMPLETED' ? 'bg-[#217346] text-white' :
                                                        opp.workflow_status === 'UNDER_ASSESSMENT' ? 'bg-[#E27D12] text-white' :
                                                            opp.workflow_status === 'ASSIGNED_TO_SA' ? 'bg-[#0073BB] text-white' :
                                                                'bg-[#F2F2F2] text-[#666666] border border-gray-300'
                                                }`}>
                                                {opp.workflow_status?.replace(/_/g, ' ') || 'COMMITTED'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 text-[#666666] italic">
                                            {new Date(opp.close_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

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
    );
}
