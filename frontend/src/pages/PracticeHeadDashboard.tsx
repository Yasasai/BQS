import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';

type TabType = 'unassigned' | 'under-assessment' | 'pending-review' | 'all';

export function PracticeHeadDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('unassigned');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<number[]>([]);

    // Mock: In real app, get from auth context
    const currentPracticeHead = "John Doe"; // Replace with actual logged-in user
    const currentPractice = "Cloud Infrastructure"; // Replace with actual user's practice

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
                // Filter to only show opportunities assigned to this practice head
                const myOpportunities = data.filter((opp: Opportunity) =>
                    opp.assigned_practice === currentPractice ||
                    opp.assigned_practice_head === currentPracticeHead
                );
                setOpportunities(myOpportunities);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    // Calculate tab counts
    const unassignedCount = opportunities.filter(o =>
        o.workflow_status === 'ASSIGNED_TO_PRACTICE' && !o.assigned_sa
    ).length;

    const underAssessmentCount = opportunities.filter(o =>
        ['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT'].includes(o.workflow_status || '')
    ).length;

    const pendingReviewCount = opportunities.filter(o =>
        o.workflow_status === 'SUBMITTED_FOR_REVIEW'
    ).length;

    // Filter opportunities based on active tab
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        if (activeTab === 'unassigned') {
            filtered = filtered.filter(o =>
                o.workflow_status === 'ASSIGNED_TO_PRACTICE' && !o.assigned_sa
            );
        } else if (activeTab === 'under-assessment') {
            filtered = filtered.filter(o =>
                ['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT'].includes(o.workflow_status || '')
            );
        } else if (activeTab === 'pending-review') {
            filtered = filtered.filter(o =>
                o.workflow_status === 'SUBMITTED_FOR_REVIEW'
            );
        }

        return filtered;
    };

    const filteredOpportunities = getFilteredOpportunities();

    // Handle assign to SA
    const handleAssignToSA = async (oppId: number, primarySA: string, secondarySA?: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/assign-sa`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    primary_sa: primarySA,
                    secondary_sa: secondarySA
                })
            });

            if (!response.ok) throw new Error('Failed to assign SA');

            alert(`Assigned to ${primarySA}`);
            fetchOpportunities();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to assign SA');
        }
    };

    // Handle review decision
    const handleReviewDecision = async (oppId: number, decision: 'APPROVED' | 'REJECTED', comments: string) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/practice-review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision, comments })
            });

            if (!response.ok) throw new Error('Failed to submit review');

            alert(`Assessment ${decision.toLowerCase()}`);
            fetchOpportunities();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit review');
        }
    };

    const getStatusBadge = (status?: string) => {
        const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
            'ASSIGNED_TO_PRACTICE': { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Needs SA Assignment' },
            'ASSIGNED_TO_SA': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'With SA' },
            'UNDER_ASSESSMENT': { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'In Progress' },
            'SUBMITTED_FOR_REVIEW': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Awaiting Review' },
            'APPROVED_BY_PRACTICE': { bg: 'bg-green-100', text: 'text-green-800', label: 'Approved' },
        };

        const config = statusConfig[status || 'ASSIGNED_TO_PRACTICE'] || statusConfig['ASSIGNED_TO_PRACTICE'];
        return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>{config.label}</span>;
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Page Title */}
                <div className="px-6 pt-6 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">Practice Head Dashboard</h1>
                    <p className="text-sm text-gray-600 mt-1">Resource Allocation & Quality Assurance - {currentPractice}</p>
                </div>

                {/* Tabs */}
                <div className="px-6">
                    <div className="flex gap-2 border-b border-gray-200">
                        <button
                            onClick={() => setActiveTab('unassigned')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${activeTab === 'unassigned' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Unassigned ({unassignedCount})
                            {unassignedCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-purple-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                    {unassignedCount}
                                </span>
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('under-assessment')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'under-assessment' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Under Assessment ({underAssessmentCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('pending-review')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${activeTab === 'pending-review' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Pending Review ({pendingReviewCount})
                            {pendingReviewCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                    {pendingReviewCount}
                                </span>
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'all' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            All ({opportunities.length})
                        </button>
                    </div>
                </div>

                {/* Action Summary */}
                <div className="px-6 py-4 bg-white border-b border-gray-200">
                    <div className="text-sm text-gray-600">
                        <span className="font-semibold text-gray-900">{filteredOpportunities.length}</span> opportunities
                        {activeTab === 'unassigned' && <span className="ml-2 text-purple-600 font-medium">→ Awaiting SA Assignment</span>}
                        {activeTab === 'pending-review' && <span className="ml-2 text-orange-600 font-medium">→ Awaiting Your Review</span>}
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
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Deal Size</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Assigned SA</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Score</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500">Loading...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500">No opportunities found</td></tr>
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
                                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 0 }).format(opp.deal_value)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {getStatusBadge(opp.workflow_status)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {opp.assigned_sa || <span className="text-gray-400 italic">Unassigned</span>}
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
                                                        {opp.workflow_status === 'ASSIGNED_TO_PRACTICE' && !opp.assigned_sa && (
                                                            <button
                                                                onClick={() => {
                                                                    setSelectedOppId([opp.id]);
                                                                    setIsAssignModalOpen(true);
                                                                    setOpenActionMenu(null);
                                                                }}
                                                                className="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-100 font-medium"
                                                            >
                                                                <UserPlus size={14} className="inline mr-2" />
                                                                Assign to SA
                                                            </button>
                                                        )}
                                                        {opp.workflow_status === 'SUBMITTED_FOR_REVIEW' && (
                                                            <>
                                                                <div className="border-t border-gray-200 my-1"></div>
                                                                <button
                                                                    onClick={() => navigate(`/score/${opp.id}`)}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100"
                                                                >
                                                                    View Assessment
                                                                </button>
                                                                <button
                                                                    onClick={() => {
                                                                        const comments = prompt('Approval Comments (optional):') || '';
                                                                        if (window.confirm('Approve this assessment and send to Management?')) {
                                                                            handleReviewDecision(opp.id, 'APPROVED', comments);
                                                                        }
                                                                    }}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100 font-medium"
                                                                >
                                                                    <CheckCircle size={14} className="inline mr-2" />
                                                                    Approve
                                                                </button>
                                                                <button
                                                                    onClick={() => {
                                                                        const comments = prompt('Rejection Reason (required):');
                                                                        if (comments && window.confirm('Reject and send back to SA for rework?')) {
                                                                            handleReviewDecision(opp.id, 'REJECTED', comments);
                                                                        }
                                                                    }}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 font-medium"
                                                                >
                                                                    <XCircle size={14} className="inline mr-2" />
                                                                    Reject (Rework)
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
