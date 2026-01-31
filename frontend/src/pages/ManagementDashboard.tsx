import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';

type TabType = 'unassigned' | 'assigned' | 'under-assessment' | 'pending-review' | 'completed' | 'accepted' | 'rejected' | 'all';

export function ManagementDashboard() {
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
        fetch('http://127.0.0.1:8000/api/opportunities')
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
        let filtered = opportunities;

        // Filter by Tab
        switch (activeTab) {
            case 'unassigned':
                filtered = filtered.filter(o => (!o.assigned_sa || o.assigned_sa === 'Unassigned') && (o.workflow_status === 'NEW' || !o.workflow_status));
                break;
            case 'assigned':
                filtered = filtered.filter(o => o.workflow_status === 'ASSIGNED_TO_SA');
                break;
            case 'under-assessment':
                filtered = filtered.filter(o => o.workflow_status === 'UNDER_ASSESSMENT');
                break;
            case 'pending-review':
                filtered = filtered.filter(o => o.workflow_status === 'SUBMITTED_FOR_REVIEW');
                break;
            case 'completed':
                filtered = filtered.filter(o => ['APPROVED', 'ACCEPTED', 'REJECTED', 'COMPLETED', 'WON', 'LOST'].includes(o.workflow_status || ''));
                break;
            case 'accepted':
                filtered = filtered.filter(o => o.workflow_status === 'APPROVED' || o.workflow_status === 'ACCEPTED');
                break;
            case 'rejected':
                filtered = filtered.filter(o => o.workflow_status === 'REJECTED');
                break;
            case 'all':
            default:
                break;
        }

        if (viewMode === 'My Team') {
            // Team filter logic placeholder
        }
        return filtered;
    };
    const filteredOpportunities = getFilteredOpportunities();

    const handleAssignToSA = async (oppId: number, primarySA: string, secondarySA?: string) => {
        console.log(`Assigning ${oppId} to ${primarySA}`);
        setIsAssignModalOpen(false);
        // Add actual API call here if needed for Management to override assignments
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar title="Executive Dashboard" />

            <div className="flex-1 px-8 py-6 max-w-[1600px] mx-auto w-full">

                {/* Header status badge placeholder */}
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-2">
                        <h1 className="text-2xl font-normal text-[#333333]">Opportunities</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-400 font-bold cursor-help">?</div>
                    </div>
                    <div className="flex items-center gap-2 bg-green-50 border border-green-200 px-3 py-1 rounded text-xs font-bold text-green-700">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        ORACLE LINKED: ACTIVE (limit=1 pattern)
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    {/* Card 1: TOTAL OPPORTUNITIES */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">TOTAL OPPORTUNITIES</div>
                        <div className="text-4xl font-normal text-[#0073BB] mb-2">{totalOpps}</div>
                        <div className="text-[12px] text-[#666666]">Active in pipeline</div>
                    </div>
                    {/* Card 2: PIPELINE VALUE */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">PIPELINE VALUE</div>
                        <div className="text-4xl font-normal text-[#217346] mb-2">${(pipelineValue / 1000000).toFixed(1)}M</div>
                        <div className="text-[12px] text-[#666666]">{formatCurrency(pipelineValue)}</div>
                    </div>
                    {/* Card 3: AVG WIN PROBABILITY */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">AVG WIN PROBABILITY</div>
                        <div className="text-4xl font-normal text-[#E27D12] mb-2">{avgWinProb}%</div>
                        <div className="text-[12px] text-[#666666]">Across all opportunities</div>
                    </div>
                    {/* Card 4: PENDING ACTIONS */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="text-[11px] font-bold text-[#666666] uppercase tracking-wider mb-4">PENDING ACTIONS</div>
                        <div className="text-4xl font-normal text-[#A80000] mb-2">{awaitingReviewCount}</div>
                        <div className="text-[12px] text-[#666666]">Awaiting your review</div>
                    </div>
                </div>

                {/* Pipeline Distribution */}
                <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200 mb-6">
                    <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">PIPELINE DISTRIBUTION BY WORKFLOW STATUS</div>
                    {/* Visual Bar */}
                    <div className="flex h-2 w-full rounded-full overflow-hidden bg-gray-100 mb-4">
                        <div style={{ width: '10%' }} className="bg-gray-400"></div>
                        <div style={{ width: '20%' }} className="bg-blue-500"></div>
                        <div style={{ width: '30%' }} className="bg-yellow-500"></div>
                        <div style={{ width: '15%' }} className="bg-red-500"></div>
                        <div style={{ width: '25%' }} className="bg-green-500"></div>
                    </div>
                    {/* Legend */}
                    <div className="flex flex-wrap gap-6 text-xs text-gray-600 font-medium">
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-gray-400"></div> NEW ({statusCounts.NEW})</div>
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500"></div> ASSIGNED TO SA ({statusCounts.ASSIGNED})</div>
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-yellow-500"></div> UNDER ASSESSMENT ({statusCounts.ASSESSMENT})</div>
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-red-500"></div> SUBMITTED FOR REVIEW ({statusCounts.REVIEW})</div>
                        <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> COMPLETED ({statusCounts.COMPLETED})</div>
                    </div>
                </div>

                {/* STATUS TABS */}
                <div className="flex border-b border-gray-200 mb-0 bg-white px-4 pt-2 rounded-t-lg items-center gap-1 overflow-x-auto border border-gray-200 border-b-0 shadow-sm">
                    {['all', 'unassigned', 'assigned', 'under-assessment', 'pending-review', 'completed', 'accepted', 'rejected'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab as TabType)}
                            className={`px-4 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors whitespace-nowrap ${activeTab === tab
                                    ? 'border-[#0073BB] text-[#0073BB]'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {tab.replace('-', ' ')}
                        </button>
                    ))}
                </div>

                {/* Optimized Toolbar */}
                <div className="flex items-center justify-between bg-white p-4 border border-gray-200 border-t-0 border-b-0 shadow-sm">
                    <div className="flex items-center gap-6">
                        <button className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                            <Filter size={18} className="text-[#666666]" /> Filters
                        </button>

                        <div className="flex items-center gap-2">
                            <span className="text-sm font-normal text-[#666666]">Find</span>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Name"
                                    className="border border-gray-300 rounded px-4 py-2 w-64 text-sm focus:outline-none focus:ring-1 focus:ring-[#0073BB]"
                                />
                                <Search size={18} className="absolute right-3 top-2.5 text-[#666666]" />
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-sm font-normal text-[#666666]">List</span>
                            <div className="relative">
                                <button className="flex items-center gap-12 px-4 py-2 text-sm font-normal text-[#333333] border border-gray-300 rounded bg-white">
                                    All Opportunities <ChevronDown size={14} className="text-[#666666]" />
                                </button>
                            </div>
                        </div>

                        <MoreHorizontal size={20} className="text-[#666666] cursor-pointer" />
                    </div>

                    <div className="flex items-center gap-3">
                        <button onClick={fetchOpportunities} className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50">
                            <RefreshCw size={18} className="text-[#666666]" /> Refresh
                        </button>

                        <div className="relative group">
                            <button className="flex items-center gap-2 px-6 py-2 text-sm font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50">
                                Actions <ChevronDown size={14} className="text-[#666666]" />
                            </button>
                        </div>

                        <button className="flex items-center gap-2 px-6 py-2 text-sm font-bold text-white bg-[#0073BB] rounded hover:bg-[#0066A3] shadow-sm transition-all">
                            Create Opportunity
                        </button>
                    </div>
                </div>

                {/* Table */}
                <div className="bg-white border border-gray-200 rounded-b-lg overflow-x-auto shadow-sm">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-[#F9FAFB]">
                            <tr>
                                <th className="px-6 py-3 text-left w-10">
                                    <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500 border-gray-300" />
                                </th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Win (%)</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Opportunity Nbr</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Name</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Owner</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Practice</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Status</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Assessment Status</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Creation Date</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Account</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Account Owner</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Amount</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Estimated Billing</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Sales Stage</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Region</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={15} className="px-6 py-12 text-center text-gray-500">Loading pipeline data...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={15} className="px-6 py-12 text-center text-gray-500">No opportunities found in this view.</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => (
                                    <tr key={opp.id} className="hover:bg-gray-50 transition-colors group cursor-pointer text-[13px] text-[#333333]" onClick={() => navigate(`/opportunity/${opp.id}`)}>
                                        <td className="px-6 py-4" onClick={e => e.stopPropagation()}>
                                            <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500 border-gray-300" />
                                        </td>
                                        <td className="px-4 py-4">
                                            <div className="bg-[#FFE57F] text-[#333333] font-bold px-2 py-0.5 rounded text-[11px] inline-block">
                                                {opp.win_probability || 0}
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.remote_id}
                                        </td>
                                        <td className="px-4 py-4 text-[#0073BB] font-normal hover:underline">
                                            {opp.name}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.sales_owner || '-'}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.practice || '-'}
                                        </td>
                                        <td className="px-4 py-4">
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-[#E8F5E9] text-[#2E7D32]">
                                                Committed
                                            </span>
                                        </td>
                                        <td className="px-4 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${opp.workflow_status === 'SUBMITTED_FOR_REVIEW' ? 'bg-[#A80000] text-white' :
                                                    (opp.workflow_status === 'APPROVED' || opp.workflow_status === 'ACCEPTED') ? 'bg-[#217346] text-white' :
                                                        opp.workflow_status === 'REJECTED' ? 'bg-gray-600 text-white' :
                                                            opp.workflow_status === 'ASSIGNED_TO_SA' ? 'bg-[#0073BB] text-white' :
                                                                opp.workflow_status === 'UNDER_ASSESSMENT' ? 'bg-[#E27D12] text-white' :
                                                                    'bg-[#F2F2F2] text-[#666666] border border-gray-300'
                                                }`}>
                                                {opp.workflow_status?.replace(/_/g, ' ') || 'Unassigned'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {new Date(opp.created_at || opp.close_date).toLocaleDateString()}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.customer}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.sales_owner || '-'}
                                        </td>
                                        <td className="px-4 py-4 text-[#333333]">
                                            {formatCurrency(opp.deal_value)}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            $0
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.sales_stage || 'PO Received'}
                                        </td>
                                        <td className="px-4 py-4 text-[#666666]">
                                            {opp.geo || '-'}
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
