import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, AlertCircle } from 'lucide-react';
import { AssignPracticeModal } from '../components/AssignPracticeModal';
import { FinalDecisionModal } from '../components/FinalDecisionModal';

type TabType = 'new-from-crm' | 'pending-final-decision' | 'completed' | 'all';

export function ManagementDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('new-from-crm');

    // Filter states
    const [selectedGeo, setSelectedGeo] = useState('All Geographies');
    const [selectedPractice, setSelectedPractice] = useState('All Practices');

    // Action menu state
    const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);

    // Modal states
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
    const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

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

    // Calculate tab counts
    const newFromCrmCount = opportunities.filter(o => o.workflow_status === 'NEW_FROM_CRM').length;
    const pendingFinalCount = opportunities.filter(o => o.workflow_status === 'PENDING_FINAL_DECISION').length;
    const completedCount = opportunities.filter(o => ['APPROVED_FINAL', 'REJECTED_FINAL'].includes(o.workflow_status || '')).length;

    // Filter opportunities based on active tab
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        if (activeTab === 'new-from-crm') {
            filtered = filtered.filter(o => o.workflow_status === 'NEW_FROM_CRM');
        } else if (activeTab === 'pending-final-decision') {
            filtered = filtered.filter(o => o.workflow_status === 'PENDING_FINAL_DECISION');
        } else if (activeTab === 'completed') {
            filtered = filtered.filter(o => ['APPROVED_FINAL', 'REJECTED_FINAL'].includes(o.workflow_status || ''));
        }

        // Apply other filters
        if (selectedGeo !== 'All Geographies') {
            filtered = filtered.filter(o => o.geo === selectedGeo);
        }
        if (selectedPractice !== 'All Practices') {
            filtered = filtered.filter(o => o.practice === selectedPractice);
        }

        return filtered;
    };

    const filteredOpportunities = getFilteredOpportunities();

    // Handle assign to practice
    const handleAssignToPractice = async (oppId: number, practice: string, practiceHead: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/assign-practice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ practice, practice_head: practiceHead })
            });

            if (!response.ok) throw new Error('Failed to assign practice');

            alert(`Assigned to ${practice} - ${practiceHead}`);
            fetchOpportunities();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to assign practice');
        }
    };

    // Handle final decision
    const handleFinalDecision = async (oppId: number, decision: 'GO' | 'NO_GO', comments: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/final-decision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision, comments })
            });

            if (!response.ok) throw new Error('Failed to submit decision');

            alert(`Final decision: ${decision}`);
            fetchOpportunities();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit decision');
        }
    };

    const getStatusBadge = (status?: string) => {
        const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
            'NEW_FROM_CRM': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'New from CRM' },
            'ASSIGNED_TO_PRACTICE': { bg: 'bg-purple-100', text: 'text-purple-800', label: 'With Practice' },
            'PENDING_FINAL_DECISION': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Awaiting Decision' },
            'APPROVED_FINAL': { bg: 'bg-green-100', text: 'text-green-800', label: 'Approved (GO)' },
            'REJECTED_FINAL': { bg: 'bg-red-100', text: 'text-red-800', label: 'Rejected (NO-GO)' },
        };

        const config = statusConfig[status || 'NEW_FROM_CRM'] || statusConfig['NEW_FROM_CRM'];
        return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>{config.label}</span>;
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Page Title */}
                <div className="px-6 pt-6 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">Management Dashboard</h1>
                    <p className="text-sm text-gray-600 mt-1">Intake Screening & Final Governance Decisions</p>
                </div>

                {/* Tabs */}
                <div className="px-6">
                    <div className="flex gap-2 border-b border-gray-200">
                        <button
                            onClick={() => setActiveTab('new-from-crm')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'new-from-crm' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            New from CRM ({newFromCrmCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('pending-final-decision')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${activeTab === 'pending-final-decision' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Pending Final Decision ({pendingFinalCount})
                            {pendingFinalCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                    {pendingFinalCount}
                                </span>
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('completed')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'completed' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Completed ({completedCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'all' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            All ({opportunities.length})
                        </button>
                    </div>
                </div>

                {/* Filters Section */}
                <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                    <div className="flex items-center gap-2 mb-3">
                        <Filter size={16} className="text-gray-500" />
                        <span className="text-sm font-semibold text-gray-700">Filters</span>
                    </div>
                    <div className="grid grid-cols-4 gap-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Geo</label>
                            <select
                                value={selectedGeo}
                                onChange={(e) => setSelectedGeo(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>All Geographies</option>
                                <option>North America</option>
                                <option>Europe</option>
                                <option>Asia Pacific</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Practice</label>
                            <select
                                value={selectedPractice}
                                onChange={(e) => setSelectedPractice(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>All Practices</option>
                                <option>Cloud Infrastructure</option>
                                <option>Cybersecurity</option>
                                <option>AI/ML</option>
                                <option>Digital Strategy</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Action Summary */}
                <div className="px-6 py-4 bg-white border-b border-gray-200">
                    <div className="text-sm text-gray-600">
                        <span className="font-semibold text-gray-900">{filteredOpportunities.length}</span> opportunities
                        {activeTab === 'new-from-crm' && <span className="ml-2 text-blue-600 font-medium">→ Awaiting Practice Assignment</span>}
                        {activeTab === 'pending-final-decision' && <span className="ml-2 text-orange-600 font-medium">→ Awaiting Your GO/NO-GO Decision</span>}
                    </div>
                </div>

                {/* Table */}
                <div className="flex-1 overflow-auto bg-white">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left w-12">
                                    <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" />
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Opp ID</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Name/Customer</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Practice</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Deal Size</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Assigned To</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Score</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={9} className="px-6 py-12 text-center text-gray-500">Loading...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={9} className="px-6 py-12 text-center text-gray-500">No opportunities found</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => (
                                    <tr key={opp.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" />
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-blue-600 hover:underline cursor-pointer" onClick={() => navigate(`/opportunity/${opp.id}`)}>
                                                {opp.remote_id || `OPP-${opp.id}`}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-sm font-medium text-gray-900">{opp.name}</div>
                                            <div className="text-sm text-gray-500">{opp.customer}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {opp.assigned_practice || opp.practice || '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 0 }).format(opp.deal_value)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {getStatusBadge(opp.workflow_status)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {opp.assigned_practice_head || opp.assigned_sa || 'Unassigned'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {opp.win_probability ? `${Math.round(opp.win_probability)}%` : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium relative">
                                            <button
                                                onClick={() => setOpenActionMenu(openActionMenu === opp.id ? null : opp.id)}
                                                className="text-gray-400 hover:text-gray-600"
                                            >
                                                <MoreHorizontal size={18} />
                                            </button>
                                            {openActionMenu === opp.id && (
                                                <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                                                    <div className="py-1">
                                                        <button
                                                            onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                        >
                                                            View Details
                                                        </button>
                                                        {opp.workflow_status === 'NEW_FROM_CRM' && (
                                                            <button
                                                                onClick={() => {
                                                                    setSelectedOpportunity(opp);
                                                                    setIsAssignModalOpen(true);
                                                                    setOpenActionMenu(null);
                                                                }}
                                                                className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100 font-medium"
                                                            >
                                                                ✓ Assign to Practice
                                                            </button>
                                                        )}
                                                        {opp.workflow_status === 'PENDING_FINAL_DECISION' && (
                                                            <>
                                                                <div className="border-t border-gray-200 my-1"></div>
                                                                <button
                                                                    onClick={() => {
                                                                        setSelectedOpportunity(opp);
                                                                        setIsDecisionModalOpen(true);
                                                                        setOpenActionMenu(null);
                                                                    }}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100 font-medium"
                                                                >
                                                                    ✓ Final Decision
                                                                </button>
                                                            </>
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modals */}
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
