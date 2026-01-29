import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { MoreHorizontal, Edit, Send, Search, RefreshCw, FileText } from 'lucide-react';

type TabType = 'my-assignments' | 'in-progress' | 'submitted' | 'all';

export function SolutionArchitectDashboard() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('my-assignments');
    const [searchTerm, setSearchTerm] = useState('');

    // Mock: In real app, get from auth context
    const currentSA = "Jane Smith";

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
    const myAssignmentsCount = opportunities.filter(o => o.workflow_status === 'ASSIGNED_TO_SA' && !o.locked_by).length;
    const inProgressCount = opportunities.filter(o => o.workflow_status === 'UNDER_ASSESSMENT').length;
    const submittedCount = opportunities.filter(o => ['SUBMITTED_FOR_REVIEW', 'APPROVED_BY_PRACTICE'].includes(o.workflow_status || '')).length;

    // Filter opportunities based on active tab & Search
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        // Tab Filter
        if (activeTab === 'my-assignments') {
            filtered = filtered.filter(o => o.workflow_status === 'ASSIGNED_TO_SA' && !o.locked_by);
        } else if (activeTab === 'in-progress') {
            filtered = filtered.filter(o => o.workflow_status === 'UNDER_ASSESSMENT');
        } else if (activeTab === 'submitted') {
            filtered = filtered.filter(o => ['SUBMITTED_FOR_REVIEW', 'APPROVED_BY_PRACTICE'].includes(o.workflow_status || ''));
        }

        // Search Filter
        if (searchTerm) {
            const lower = searchTerm.toLowerCase();
            filtered = filtered.filter(o =>
                o.name.toLowerCase().includes(lower) ||
                o.customer.toLowerCase().includes(lower) ||
                (o.remote_id && o.remote_id.toLowerCase().includes(lower))
            );
        }

        return filtered;
    };

    const filteredOpportunities = getFilteredOpportunities();

    const handleStartAssessment = async (oppId: number) => {
        try {
            await fetch(`http://localhost:8000/api/opportunities/${oppId}/start-assessment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sa_name: currentSA }) // Simplified body
            });
            navigate(`/score-opportunity/${oppId}`);
        } catch (error) {
            console.error('Error:', error);
            navigate(`/score-opportunity/${oppId}`); // Proceed even if API fails (mock handling)
        }
    };

    return (
        <div className="min-h-screen bg-[#FDF3E1] flex flex-col font-sans text-[#333333]">
            <TopBar />

            <div className="flex flex-col flex-1 px-8 py-6 max-w-[1600px] mx-auto w-full">
                {/* Page Title Section */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-normal text-[#333333]">Architect Execution</h1>
                        <p className="text-xs text-[#666666] uppercase font-bold tracking-widest mt-1">Qualification & Scoring Workbench</p>
                    </div>
                    <div className="flex items-center gap-2 bg-[#E7F0F7] px-4 py-1.5 rounded-full border border-[#D0E1EE]">
                        <div className="w-2 h-2 bg-[#0073BB] rounded-full"></div>
                        <span className="text-[11px] font-bold text-[#0073BB] uppercase">Assigned User: {currentSA}</span>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    {/* Premium Tabs */}
                    <div className="flex border-b border-gray-100 bg-[#F9FAFB]">
                        <button
                            onClick={() => setActiveTab('my-assignments')}
                            className={`px-8 py-4 text-xs font-bold uppercase tracking-widest transition-all relative ${activeTab === 'my-assignments' ? 'text-[#0073BB] bg-white' : 'text-[#666666] hover:bg-white/50'}`}
                        >
                            <div className="flex items-center gap-2">
                                ATTACHED OPPORTUNITIES
                                {myAssignmentsCount > 0 && (
                                    <span className="bg-[#A80000] text-white text-[9px] px-1.5 py-0.5 rounded-full">
                                        {myAssignmentsCount}
                                    </span>
                                )}
                            </div>
                            {activeTab === 'my-assignments' && <div className="absolute bottom-0 left-0 w-full h-1 bg-[#0073BB]"></div>}
                        </button>
                        <button
                            onClick={() => setActiveTab('in-progress')}
                            className={`px-8 py-4 text-xs font-bold uppercase tracking-widest transition-all relative ${activeTab === 'in-progress' ? 'text-[#E27D12] bg-white' : 'text-[#666666] hover:bg-white/50'}`}
                        >
                            IN PROGRESS ({inProgressCount})
                            {activeTab === 'in-progress' && <div className="absolute bottom-0 left-0 w-full h-1 bg-[#E27D12]"></div>}
                        </button>
                        <button
                            onClick={() => setActiveTab('submitted')}
                            className={`px-8 py-4 text-xs font-bold uppercase tracking-widest transition-all relative ${activeTab === 'submitted' ? 'text-[#217346] bg-white' : 'text-[#666666] hover:bg-white/50'}`}
                        >
                            SUBMITTED ({submittedCount})
                            {activeTab === 'submitted' && <div className="absolute bottom-0 left-0 w-full h-1 bg-[#217346]"></div>}
                        </button>
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-8 py-4 text-xs font-bold uppercase tracking-widest transition-all relative ${activeTab === 'all' ? 'text-[#333333] bg-white' : 'text-[#666666] hover:bg-white/50'}`}
                        >
                            FULL REGISTRY
                            {activeTab === 'all' && <div className="absolute bottom-0 left-0 w-full h-1 bg-[#333333]"></div>}
                        </button>
                    </div>

                    {/* Toolbar Section */}
                    <div className="p-4 bg-white border-b border-gray-100 flex justify-between items-center">
                        <div className="flex items-center gap-4 bg-[#F9FAFB] border border-gray-300 rounded px-4 py-2 w-96 transition-all focus-within:border-[#0073BB] focus-within:shadow-sm">
                            <Search className="text-[#666666]" size={16} />
                            <input
                                type="text"
                                placeholder="Locate engagement, account..."
                                className="bg-transparent border-none w-full text-sm focus:outline-none placeholder:text-gray-400 font-medium"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] font-bold text-[#666666] uppercase tracking-wide">Registry Count</span>
                                <span className="text-sm font-bold text-[#333333]">{filteredOpportunities.length} ITEMS</span>
                            </div>
                            <button onClick={fetchOpportunities} className="p-2 text-[#666666] hover:text-[#0073BB] transition-colors rounded-lg hover:bg-gray-50 border border-gray-200">
                                <RefreshCw size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Interactive Table Area */}
                    <div className="overflow-x-auto min-h-[400px]">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-32 bg-white">
                                <RefreshCw size={32} className="text-[#0073BB] animate-spin mb-4" />
                                <span className="text-xs font-bold text-[#666666] tracking-widest uppercase">Fetching Assignments...</span>
                            </div>
                        ) : filteredOpportunities.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-32 bg-white">
                                <div className="bg-[#FDF3E1] p-6 rounded-full mb-4">
                                    <FileText size={48} className="text-[#E27D12]/40" />
                                </div>
                                <h3 className="text-lg font-normal text-[#333333]">No Active Assignments</h3>
                                <p className="text-sm text-[#666666] mt-1">Review later for new qualification requests from Leadership.</p>
                            </div>
                        ) : (
                            <table className="min-w-full divide-y divide-gray-100">
                                <thead className="bg-[#F9FAFB]">
                                    <tr>
                                        <th className="px-6 py-4 text-left w-10"><input type="checkbox" className="rounded" /></th>
                                        <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Opportunity Detail</th>
                                        <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Account</th>
                                        <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Project Value</th>
                                        <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Workflow Status</th>
                                        <th className="px-4 py-4 text-left text-[11px] font-bold text-[#666666] uppercase tracking-wider">Initiator</th>
                                        <th className="px-4 py-4 text-right text-[11px] font-bold text-[#666666] uppercase tracking-wider">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-100">
                                    {filteredOpportunities.map((opp) => (
                                        <tr key={opp.id} className="hover:bg-blue-50/30 transition-colors group cursor-pointer" onClick={() => handleStartAssessment(opp.id)}>
                                            <td className="px-6 py-4" onClick={e => e.stopPropagation()}><input type="checkbox" className="rounded" /></td>
                                            <td className="px-4 py-4">
                                                <div className="text-sm font-semibold text-[#0073BB] group-hover:underline decoration-1 underline-offset-4">{opp.name}</div>
                                                <div className="text-[11px] font-bold text-[#666666] mt-0.5">{opp.remote_id}</div>
                                            </td>
                                            <td className="px-4 py-4 text-sm font-medium text-[#333333]">{opp.customer}</td>
                                            <td className="px-4 py-4 text-sm font-bold text-[#217346]">
                                                {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 0 }).format(opp.deal_value)}
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
                                            <td className="px-4 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-[10px] text-gray-500 font-bold border border-gray-200">
                                                        {opp.assigned_practice_head?.charAt(0) || 'P'}
                                                    </div>
                                                    <span className="text-xs font-medium text-[#666666]">{opp.assigned_practice_head || 'Practice Head'}</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4 text-right">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); handleStartAssessment(opp.id); }}
                                                    className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-white border border-gray-300 text-[#333333] hover:border-[#0073BB] hover:text-[#0073BB] transition-all shadow-sm"
                                                >
                                                    {opp.workflow_status === 'ASSIGNED_TO_SA' ? 'Run Assessment' : 'Restore Session'}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
