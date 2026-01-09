import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { MoreHorizontal, Edit, Send } from 'lucide-react';
import { ScoringWizard } from '../components/ScoringWizard';

type TabType = 'my-assignments' | 'in-progress' | 'submitted' | 'all';

export function SolutionArchitectDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('my-assignments');

    // Modal state
    const [isWizardOpen, setIsWizardOpen] = useState(false);
    const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

    // Mock: In real app, get from auth context
    const currentSA = "Jane Smith"; // Replace with actual logged-in user

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
                // Filter to only show opportunities assigned to this SA
                const myOpportunities = data.filter((opp: Opportunity) =>
                    opp.assigned_sa === currentSA ||
                    opp.assigned_sa_secondary === currentSA
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
    const myAssignmentsCount = opportunities.filter(o =>
        o.workflow_status === 'ASSIGNED_TO_SA' && !o.locked_by
    ).length;

    const inProgressCount = opportunities.filter(o =>
        o.workflow_status === 'UNDER_ASSESSMENT'
    ).length;

    const submittedCount = opportunities.filter(o =>
        ['SUBMITTED_FOR_REVIEW', 'APPROVED_BY_PRACTICE'].includes(o.workflow_status || '')
    ).length;

    // Filter opportunities based on active tab
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        if (activeTab === 'my-assignments') {
            filtered = filtered.filter(o =>
                o.workflow_status === 'ASSIGNED_TO_SA' && !o.locked_by
            );
        } else if (activeTab === 'in-progress') {
            filtered = filtered.filter(o =>
                o.workflow_status === 'UNDER_ASSESSMENT'
            );
        } else if (activeTab === 'submitted') {
            filtered = filtered.filter(o =>
                ['SUBMITTED_FOR_REVIEW', 'APPROVED_BY_PRACTICE'].includes(o.workflow_status || '')
            );
        }

        return filtered;
    };

    const filteredOpportunities = getFilteredOpportunities();

    // Handle start assessment
    const handleStartAssessment = async (oppId: number) => {
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${oppId}/start-assessment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sa_name: currentSA })
            });

            if (!response.ok) throw new Error('Failed to start assessment');

            // Navigate to assessment form
            navigate(`/score/${oppId}`);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to start assessment');
        }
    };

    const getStatusBadge = (status?: string, lockedBy?: string) => {
        if (lockedBy && lockedBy !== currentSA) {
            return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">🔒 Locked by {lockedBy}</span>;
        }

        const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
            'ASSIGNED_TO_SA': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'New Assignment' },
            'UNDER_ASSESSMENT': { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'In Progress' },
            'SUBMITTED_FOR_REVIEW': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Under Review' },
            'APPROVED_BY_PRACTICE': { bg: 'bg-green-100', text: 'text-green-800', label: 'Approved' },
        };

        const config = statusConfig[status || 'ASSIGNED_TO_SA'] || statusConfig['ASSIGNED_TO_SA'];
        return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>{config.label}</span>;
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Page Title */}
                <div className="px-6 pt-6 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">Solution Architect Dashboard</h1>
                    <p className="text-sm text-gray-600 mt-1">Assessment Execution - {currentSA}</p>
                </div>

                {/* Tabs */}
                <div className="px-6">
                    <div className="flex gap-2 border-b border-gray-200">
                        <button
                            onClick={() => setActiveTab('my-assignments')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${activeTab === 'my-assignments' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            My Assignments ({myAssignmentsCount})
                            {myAssignmentsCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-blue-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                    {myAssignmentsCount}
                                </span>
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('in-progress')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'in-progress' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            In Progress ({inProgressCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('submitted')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'submitted' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'}`}
                        >
                            Submitted ({submittedCount})
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
                        {activeTab === 'my-assignments' && <span className="ml-2 text-blue-600 font-medium">→ Ready for Assessment</span>}
                        {activeTab === 'in-progress' && <span className="ml-2 text-indigo-600 font-medium">→ Complete & Submit for Review</span>}
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
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Assigned By</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500">Loading...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={8} className="px-6 py-12 text-center text-gray-500">No opportunities assigned to you</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => {
                                    const isLocked = opp.locked_by && opp.locked_by !== currentSA;
                                    const canEdit = !isLocked && ['ASSIGNED_TO_SA', 'UNDER_ASSESSMENT'].includes(opp.workflow_status || '');

                                    return (
                                        <tr key={opp.id} className={`hover:bg-gray-50 transition-colors ${isLocked ? 'opacity-60' : ''}`}>
                                            <td className="px-6 py-4">
                                                <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" disabled={isLocked} />
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
                                                {opp.assigned_practice || '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 0 }).format(opp.deal_value)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                {getStatusBadge(opp.workflow_status, opp.locked_by)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {opp.assigned_practice_head || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium relative">
                                                <button
                                                    onClick={() => setOpenActionMenu(openActionMenu === opp.id ? null : opp.id)}
                                                    className="text-gray-400 hover:text-gray-600"
                                                    disabled={isLocked}
                                                >
                                                    <MoreHorizontal size={18} />
                                                </button>
                                                {openActionMenu === opp.id && !isLocked && (
                                                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                                                        <div className="py-1">
                                                            <button
                                                                onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                            >
                                                                View Details
                                                            </button>
                                                            {opp.workflow_status === 'ASSIGNED_TO_SA' && (
                                                                <button
                                                                    onClick={() => {
                                                                        setSelectedOpportunity(opp);
                                                                        handleStartAssessment(opp.id).then(() => {
                                                                            setIsWizardOpen(true);
                                                                            setOpenActionMenu(null);
                                                                        });
                                                                    }}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100 font-medium"
                                                                >
                                                                    <Edit size={14} className="inline mr-2" />
                                                                    Start Assessment
                                                                </button>
                                                            )}
                                                            {opp.workflow_status === 'UNDER_ASSESSMENT' && (
                                                                <>
                                                                    <button
                                                                        onClick={() => {
                                                                            setSelectedOpportunity(opp);
                                                                            setIsWizardOpen(true);
                                                                            setOpenActionMenu(null);
                                                                        }}
                                                                        className="block w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-gray-100 font-medium"
                                                                    >
                                                                        <Edit size={14} className="inline mr-2" />
                                                                        Continue Assessment
                                                                    </button>
                                                                </>
                                                            )}
                                                            {opp.workflow_status === 'SUBMITTED_FOR_REVIEW' && (
                                                                <button
                                                                    onClick={() => {
                                                                        setSelectedOpportunity(opp);
                                                                        setIsWizardOpen(true);
                                                                        setOpenActionMenu(null);
                                                                    }}
                                                                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                                >
                                                                    View Submitted Assessment
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modals */}
            {selectedOpportunity && (
                <ScoringWizard
                    opportunity={selectedOpportunity}
                    isOpen={isWizardOpen}
                    onClose={() => setIsWizardOpen(false)}
                    onSuccess={fetchOpportunities}
                />
            )}
        </div>
    );
}
