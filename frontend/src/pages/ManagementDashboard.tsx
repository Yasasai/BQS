import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { HelpCircle, Search, ChevronDown, MoreHorizontal } from 'lucide-react';
import { TopBar } from '../components/TopBar';
import { AssignPracticeModal } from '../components/AssignPracticeModal';
import { FinalDecisionModal } from '../components/FinalDecisionModal';
import { SyncStatusPopup } from '../components/SyncStatusPopup';
import { Terminal } from 'lucide-react';

type ListFilter = 'All Opportunities' | 'Approved by Practice' | 'Still with Practice';

export function ManagementDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [listFilter, setListFilter] = useState<ListFilter>('All Opportunities');

    // Modal states
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
    const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);
    const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
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

    const formatCurrency = (amount: number, currency: string = 'USD') => {
        const symbols: Record<string, string> = { 'SAR': 'ر.س', 'INR': 'Rs', 'PHP': 'Php', 'GBP': '£' };
        const symbol = symbols[currency] || '$';
        const formattedAmount = new Intl.NumberFormat('en-US').format(amount);
        if (currency === 'SAR') return `${formattedAmount} ${symbol}`;
        return `${symbol}${formattedAmount}`;
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return '-';
        const d = new Date(dateString);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${d.getDate().toString().padStart(2, '0')}-${months[d.getMonth()]}-${d.getFullYear()}`;
    };

    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        if (listFilter === 'Approved by Practice') {
            filtered = filtered.filter(o => o.workflow_status === 'PENDING_GOVERNANCE' || o.workflow_status === 'PENDING_FINAL_DECISION');
        } else if (listFilter === 'Still with Practice') {
            filtered = filtered.filter(o => ['ASSIGNED_TO_PRACTICE', 'PENDING_ASSESSMENT', 'UNDER_ASSESSMENT', 'REVIEW_PENDING'].includes(o.workflow_status || ''));
        }

        // Filter out opportunities that are closed in CRM
        filtered = filtered.filter(o => o.workflow_status !== 'CLOSED_IN_CRM');

        if (searchQuery) {
            filtered = filtered.filter(o =>
                o.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                o.remote_id.includes(searchQuery)
            );
        }

        return filtered;
    };

    const filteredOpps = getFilteredOpportunities();

    return (
        <div className="min-h-screen bg-white flex flex-col font-['Open_Sans',_Tahoma,_sans-serif] text-[12px] text-gray-800">
            <TopBar />

            {/* Header Controls Area */}
            <div className="bg-white px-4 py-4 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                        <h1 className="text-xl font-normal text-gray-700">Management Insights & Decisions</h1>
                        <HelpCircle size={14} className="text-gray-400 cursor-help" />
                    </div>

                    {/* CRM Sync Button */}
                    <button
                        onClick={() => setIsSyncModalOpen(true)}
                        className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded font-bold hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20"
                    >
                        <Terminal size={14} />
                        CRM Sync Status
                    </button>
                </div>

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        {/* Find Section */}
                        <div className="flex items-center gap-2">
                            <span className="text-gray-600">Find</span>
                            <div className="flex border border-gray-300 rounded shadow-sm bg-white overflow-hidden">
                                <div className="px-2 py-1 bg-gray-50 border-r border-gray-300 flex items-center gap-1">
                                    <span>Name</span>
                                </div>
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="px-3 py-1 focus:outline-none w-48 text-gray-700"
                                />
                                <button className="px-2 py-1 border-l border-gray-300 hover:bg-gray-50 flex items-center justify-center">
                                    <Search size={14} className="text-gray-500" />
                                </button>
                            </div>
                        </div>

                        {/* List Section */}
                        <div className="flex items-center gap-2">
                            <span className="text-gray-600">List</span>
                            <div className="relative">
                                <select
                                    value={listFilter}
                                    onChange={(e) => setListFilter(e.target.value as ListFilter)}
                                    className="appearance-none border border-gray-300 rounded px-3 py-1 pr-10 bg-white shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-400 w-52"
                                >
                                    <option>All Opportunities</option>
                                    <option>Approved by Practice</option>
                                    <option>Still with Practice</option>
                                </select>
                                <ChevronDown size={14} className="absolute right-3 top-2 text-gray-400 pointer-events-none" />
                            </div>
                        </div>
                    </div>

                    {/* Actions Area */}
                    <div className="flex items-center gap-2 pr-2 border-l border-gray-200 pl-4">
                        <button className="flex items-center gap-4 px-4 py-1.5 border border-gray-300 rounded bg-white hover:bg-gray-50 text-gray-700 shadow-sm transition-all group">
                            Actions
                            <ChevronDown size={14} className="text-gray-400 group-hover:text-gray-600" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Table Area */}
            <div className="flex-1 overflow-auto">
                <table className="min-w-full border-collapse">
                    <thead className="sticky top-0 bg-white border-b border-gray-200">
                        <tr className="text-black font-bold text-left bg-[#F8F9FA]">
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[100px]">Win (%)</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[120px]">Opp Num</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[250px]">Name</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[150px]">Owner</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[150px]">Practice</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[150px]">Status</th>
                            <th className="px-4 py-3 border-r border-gray-100 min-w-[150px]">Amount</th>
                            <th className="px-4 py-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500 italic">Synchronizing CRM data...</td></tr>
                        ) : filteredOpps.length === 0 ? (
                            <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500 border-t border-gray-100">No data found.</td></tr>
                        ) : (
                            filteredOpps.map((opp) => (
                                <tr key={opp.id} className="border-b border-gray-50 hover:bg-blue-50/10 transition-colors">
                                    <td className="px-4 py-2.5">
                                        <div className="w-10 h-5 bg-green-700 text-white flex items-center justify-center rounded-full text-[10px] font-bold">
                                            {opp.win_probability || 0}
                                        </div>
                                    </td>
                                    <td className="px-4 py-2.5 text-blue-600 hover:underline cursor-pointer" onClick={() => navigate(`/opportunity/${opp.id}`)}>
                                        {opp.remote_id}
                                    </td>
                                    <td className="px-4 py-2.5 text-blue-600 hover:underline cursor-pointer font-medium" onClick={() => navigate(`/opportunity/${opp.id}`)}>
                                        {opp.name}
                                    </td>
                                    <td className="px-4 py-2.5 text-blue-600 hover:underline cursor-pointer">
                                        {opp.sales_owner || '-'}
                                    </td>
                                    <td className="px-4 py-2.5 text-gray-600">
                                        {opp.practice || opp.assigned_practice || '-'}
                                    </td>
                                    <td className="px-4 py-2.5 text-gray-600">
                                        {opp.workflow_status === 'PENDING_GOVERNANCE' || opp.workflow_status === 'PENDING_FINAL_DECISION'
                                            ? 'Approved by Practice'
                                            : opp.workflow_status?.replace(/_/g, ' ') || 'New'}
                                    </td>
                                    <td className="px-4 py-2.5 text-gray-700 font-semibold tracking-tight">
                                        {formatCurrency(opp.deal_value || 0, opp.currency)}
                                    </td>
                                    <td className="px-4 py-2.5 text-right relative">
                                        <button
                                            onClick={() => setOpenActionMenu(openActionMenu === opp.id ? null : opp.id)}
                                            className="text-gray-400 hover:text-gray-600 p-1 hover:bg-gray-100 rounded"
                                        >
                                            <MoreHorizontal size={14} />
                                        </button>
                                        {openActionMenu === opp.id && (
                                            <div className="absolute right-4 mt-1 w-48 bg-white border border-gray-200 rounded shadow-xl z-50 py-1 text-left overflow-hidden translate-y-0">
                                                <button onClick={() => navigate(`/opportunity/${opp.id}`)} className="block w-full px-4 py-2 hover:bg-gray-50">View Details</button>
                                                {opp.remote_url && (
                                                    <a
                                                        href={opp.remote_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="block w-full px-4 py-2 hover:bg-gray-50 text-blue-600 border-b border-gray-100"
                                                    >
                                                        View in Oracle CRM
                                                    </a>
                                                )}
                                                {opp.workflow_status === 'NEW_FROM_CRM' && (
                                                    <button onClick={() => { setSelectedOpportunity(opp); setIsAssignModalOpen(true); setOpenActionMenu(null); }} className="block w-full px-4 py-2 hover:bg-gray-50 text-blue-600 font-medium">Assign to Practice</button>
                                                )}
                                                {opp.workflow_status === 'READY_FOR_MGMT_REVIEW' && (
                                                    <button onClick={() => { setSelectedOpportunity(opp); setIsDecisionModalOpen(true); setOpenActionMenu(null); }} className="block w-full px-4 py-2 hover:bg-gray-50 text-green-600 font-medium">Review Bid (GO/NO-GO)</button>
                                                )}
                                                {(opp.workflow_status === 'PENDING_GOVERNANCE' || opp.workflow_status === 'PENDING_FINAL_DECISION') && (
                                                    <button onClick={() => { setSelectedOpportunity(opp); setIsDecisionModalOpen(true); setOpenActionMenu(null); }} className="block w-full px-4 py-2 hover:bg-gray-50 text-green-600 font-medium">Final GO/NO-GO</button>
                                                )}
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <SyncStatusPopup
                isOpen={isSyncModalOpen}
                onClose={() => setIsSyncModalOpen(false)}
            />

            {selectedOpportunity && (
                <>
                    <AssignPracticeModal
                        opportunity={selectedOpportunity}
                        isOpen={isAssignModalOpen}
                        onClose={() => setIsAssignModalOpen(false)}
                        onSuccess={fetchOpportunities}
                    />
                    <FinalDecisionModal
                        opportunity={selectedOpportunity}
                        isOpen={isDecisionModalOpen}
                        onClose={() => setIsDecisionModalOpen(false)}
                        onSuccess={fetchOpportunities}
                    />
                </>
            )}
        </div>
    );
}

