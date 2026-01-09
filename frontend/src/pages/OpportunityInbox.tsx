import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { ChevronDown, MoreHorizontal, Filter } from 'lucide-react';

type TabType = 'inbox' | 'evaluation' | 'governance' | 'solutioning' | 'all';


export function OpportunityInbox() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('all');

    // Filter states
    const [selectedGeo, setSelectedGeo] = useState('All Geographies');
    const [selectedPractice, setSelectedPractice] = useState('All Practices');
    const [selectedDealSize, setSelectedDealSize] = useState('Any Deal Size');
    const [selectedAge, setSelectedAge] = useState('Any Age');

    // Action menu state
    const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);

    // Assign modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [selectedOpportunityForAssign, setSelectedOpportunityForAssign] = useState<number | null>(null);

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




    // Calculate tab counts based on governance stages
    const inboxCount = opportunities.filter(o =>
        ['Inbox/Screening', 'Stakeholder Assignment', 'CRM Qualification'].includes(o.current_stage || 'Inbox/Screening')
    ).length;

    const evaluationCount = opportunities.filter(o =>
        o.current_stage === 'Evaluation Cycle'
    ).length;

    const governanceCount = opportunities.filter(o =>
        ['Governance Review', 'Feasibility/Due Diligence'].includes(o.current_stage || '')
    ).length;

    const solutioningCount = opportunities.filter(o =>
        ['Solutioning', 'Closure'].includes(o.current_stage || '')
    ).length;

    // Filter opportunities based on active tab
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        if (activeTab === 'inbox') {
            filtered = filtered.filter(o =>
                ['Inbox/Screening', 'Stakeholder Assignment', 'CRM Qualification'].includes(o.current_stage || 'Inbox/Screening')
            );
        } else if (activeTab === 'evaluation') {
            filtered = filtered.filter(o => o.current_stage === 'Evaluation Cycle');
        } else if (activeTab === 'governance') {
            filtered = filtered.filter(o =>
                ['Governance Review', 'Feasibility/Due Diligence'].includes(o.current_stage || '')
            );
        } else if (activeTab === 'solutioning') {
            filtered = filtered.filter(o =>
                ['Solutioning', 'Closure'].includes(o.current_stage || '')
            );
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


    // Calculate age in days
    const calculateAge = (lastSynced: string) => {
        const syncDate = new Date(lastSynced);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - syncDate.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    };

    // Calculate hours in current stage
    const calculateStageHours = (stageEnteredAt?: string) => {
        if (!stageEnteredAt) return 0;
        const enteredDate = new Date(stageEnteredAt);
        const now = new Date();
        const diffTime = Math.abs(now.getTime() - enteredDate.getTime());
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        return diffHours;
    };

    // Check if opportunity is stuck (>48 hours in critical stages)
    const isStuck = (opp: Opportunity) => {
        const criticalStages = ['Evaluation Cycle', 'Governance Review'];
        const hoursInStage = calculateStageHours(opp.stage_entered_at);
        return criticalStages.includes(opp.current_stage || '') && hoursInStage > 48;
    };

    // Count stuck opportunities
    const stuckCount = opportunities.filter(isStuck).length;


    // Handle assign owner
    const handleOpenAssignModal = (oppId: number) => {
        setSelectedOpportunityForAssign(oppId);
        setIsAssignModalOpen(true);
        setOpenActionMenu(null); // Close action menu
    };

    const handleAssign = async (assignmentData: AssignmentData) => {
        if (!selectedOpportunityForAssign) return;

        console.log('Assigning to opportunity:', selectedOpportunityForAssign, assignmentData);

        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${selectedOpportunityForAssign}/assign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(assignmentData)
            });

            if (!response.ok) {
                throw new Error('Failed to assign Solution Architect');
            }

            const result = await response.json();
            console.log('Assignment result:', result);

            // Refresh opportunities
            fetchOpportunities();

            // Close modal
            setIsAssignModalOpen(false);
            setSelectedOpportunityForAssign(null);

            alert(`Solution Architect "${assignmentData.primarySA}" assigned successfully!`);
        } catch (error) {
            console.error('Error assigning Solution Architect:', error);
            alert('Failed to assign Solution Architect. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Page Title */}
                <div className="px-6 pt-6 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">Bid Governance & Execution Dashboard</h1>
                    <p className="text-sm text-gray-600 mt-1">Track opportunities through the 8-stage governance pipeline</p>
                </div>

                {/* Tabs */}
                <div className="px-6">
                    <div className="flex gap-2 border-b border-gray-200">
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'all'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            All ({opportunities.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('inbox')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'inbox'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            Inbox ({inboxCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('evaluation')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'evaluation'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            Evaluation ({evaluationCount})
                        </button>
                        <button
                            onClick={() => setActiveTab('governance')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors relative ${activeTab === 'governance'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            Governance ({governanceCount})
                            {stuckCount > 0 && (
                                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                                    {stuckCount}
                                </span>
                            )}
                        </button>
                        <button
                            onClick={() => setActiveTab('solutioning')}
                            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'solutioning'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            Solutioning ({solutioningCount})
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
                                <option>Latin America</option>
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
                                <option>Cloud Infra</option>
                                <option>Digital Strategy</option>
                                <option>Cybersecurity</option>
                                <option>AI/ML</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Deal Size</label>
                            <select
                                value={selectedDealSize}
                                onChange={(e) => setSelectedDealSize(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>Any Deal Size</option>
                                <option>&lt; $100K</option>
                                <option>$100K - $500K</option>
                                <option>$500K - $1M</option>
                                <option>&gt; $1M</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Age</label>
                            <select
                                value={selectedAge}
                                onChange={(e) => setSelectedAge(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>Any Age</option>
                                <option>&lt; 7 days</option>
                                <option>7-30 days</option>
                                <option>30-90 days</option>
                                <option>&gt; 90 days</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="px-6 py-4 bg-white border-b border-gray-200 flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                        <span className="font-semibold text-gray-900">{filteredOpportunities.length}</span> opportunities in {activeTab === 'all' ? 'pipeline' : activeTab + ' stage'}.
                        {stuckCount > 0 && <span className="ml-2 text-red-600 font-medium">⚠ {stuckCount} stuck (&gt;48hrs)</span>}
                    </div>
                    <div className="flex gap-2">
                        <button className="px-4 py-2 bg-white border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm flex items-center gap-2">
                            More Actions <ChevronDown size={14} />
                        </button>
                    </div>
                </div>

                {/* Table Header Description */}
                <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
                    <h2 className="text-base font-semibold text-gray-900">
                        {activeTab === 'all' ? 'All Opportunities' :
                            activeTab === 'inbox' ? 'Inbox & Initial Screening' :
                                activeTab === 'evaluation' ? 'Evaluation Cycle' :
                                    activeTab === 'governance' ? 'Governance & Feasibility Review' :
                                        'Solutioning & Closure'}
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        {activeTab === 'all' ? 'Complete pipeline view across all stages.' :
                            activeTab === 'inbox' ? 'Opportunities awaiting management approval, stakeholder assignment, or CRM qualification.' :
                                activeTab === 'evaluation' ? 'Opportunities undergoing scoring, win probability assessment, and budget alignment.' :
                                    activeTab === 'governance' ? 'Opportunities pending leadership Go/No-Go decision or feasibility checks.' :
                                        'Opportunities in requirements design, prototyping, proposal submission, or contract negotiation.'}
                    </p>
                </div>

                {/* Table Section */}
                <div className="flex-1 overflow-auto bg-white">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left w-12">
                                    <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" />
                                </th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Opp ID</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Name/Customer</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Practice</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Deal Size</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Win Prob</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Current Stage</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Governance Status</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Pending With</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Stage Duration</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={11} className="px-6 py-12 text-center text-gray-500">Loading opportunities...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={11} className="px-6 py-12 text-center text-gray-500">No opportunities found.</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => {
                                    const stuck = isStuck(opp);
                                    const stageHours = calculateStageHours(opp.stage_entered_at);

                                    return (
                                        <tr key={opp.id} className={`hover:bg-gray-50 transition-colors ${stuck ? 'bg-red-50' : ''}`}>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4" />
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div
                                                    onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                    className="text-sm font-medium text-blue-600 hover:underline cursor-pointer"
                                                >
                                                    {opp.remote_id || `OPP-${opp.id}`}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-medium text-gray-900">{opp.name}</div>
                                                <div className="text-sm text-gray-500">{opp.customer}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {opp.practice || '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 0 }).format(opp.deal_value)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {opp.win_probability ? `${Math.round(opp.win_probability)}%` : '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                    {opp.current_stage || 'Inbox/Screening'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${opp.governance_status === 'Approved' ? 'bg-green-100 text-green-800' :
                                                    opp.governance_status === 'Rejected' ? 'bg-red-100 text-red-800' :
                                                        opp.governance_status === 'On-Hold' ? 'bg-yellow-100 text-yellow-800' :
                                                            'bg-orange-100 text-orange-800'
                                                    }`}>
                                                    {opp.governance_status || 'Pending'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {opp.pending_with || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                <span className={stuck ? 'text-red-600 font-semibold' : 'text-gray-600'}>
                                                    {stageHours}h {stuck && '⚠'}
                                                </span>
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
                                                            <button
                                                                onClick={() => handleOpenAssignModal(opp.id)}
                                                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                            >
                                                                Assign Stakeholder
                                                            </button>
                                                            <button
                                                                onClick={() => navigate(`/score/${opp.id}`)}
                                                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                            >
                                                                Start Assessment
                                                            </button>
                                                            <div className="border-t border-gray-200 my-1"></div>
                                                            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                                                Move to Next Stage
                                                            </button>
                                                            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                                                Update Governance Status
                                                            </button>
                                                            <div className="border-t border-gray-200 my-1"></div>
                                                            <button className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                                                                Delete
                                                            </button>
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

            {/* Assign Architect Modal */}
            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                onAssign={handleAssign}
                opportunityIds={selectedOpportunityForAssign ? [selectedOpportunityForAssign] : []}
            />
        </div>
    );
}
