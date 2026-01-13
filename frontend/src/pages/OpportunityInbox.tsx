import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { ActionColumn } from '../components/ActionColumn';
import { ChevronDown, Filter, Info } from 'lucide-react';
import { useUser } from '../context/UserContext';

export function OpportunityInbox() {
    const navigate = useNavigate();
    const { currentUser } = useUser();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('all');

    // Filter states
    const [selectedGeo, setSelectedGeo] = useState('All Geographies');
    const [selectedPractice, setSelectedPractice] = useState('All Practices');

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
                // Map data to ensure statuses match for demo if needed
                const mappedData = data.map((opp: any) => ({
                    ...opp,
                    // If no status, default to something sensible for demo
                    status: opp.status || 'New from CRM'
                }));
                setOpportunities(mappedData);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    const handleAction = (action: string, opp: Opportunity) => {
        console.log(`Action: ${action} on Opportunity: ${opp.id}`);
        if (action === 'ASSIGN_TO_SA') {
            setSelectedOpportunityForAssign(opp.id);
            setIsAssignModalOpen(true);
        } else if (action === 'START_ASSESSMENT' || action === 'SAVE_DRAFT') {
            navigate(`/score/${opp.id}`);
        } else if (action === 'SUBMIT_SCORE' || action === 'APPROVE_FOR_BID') {
            // Mock update for demo
            alert(`${action} performed on ${opp.name}`);
            fetchOpportunities();
        } else {
            alert(`${action} action triggered for ${opp.name}`);
        }
    };

    const handleAssign = async (assignmentData: AssignmentData) => {
        if (!selectedOpportunityForAssign) return;
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${selectedOpportunityForAssign}/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(assignmentData)
            });
            if (!response.ok) throw new Error('Failed to assign');
            fetchOpportunities();
            setIsAssignModalOpen(false);
            setSelectedOpportunityForAssign(null);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const getDashboardTitle = () => {
        if (currentUser.role === 'MANAGEMENT') return "Management Dashboard";
        if (currentUser.role === 'SOLUTION_ARCHITECT') return "Solution Architect 'Assigned to Me' Inbox";
        return "Bid Governance & Execution Dashboard";
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Page Title */}
                <div className="px-6 pt-6 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">{getDashboardTitle()}</h1>
                    <p className="text-sm text-gray-600 mt-1">
                        {currentUser.role === 'PRACTICE_HEAD' ? 'Track opportunities through the 8-stage governance pipeline' :
                            currentUser.role === 'SOLUTION_ARCHITECT' ? 'Assess and score your assigned technical solutions' :
                                'High-level oversight and final bid approvals'}
                    </p>
                </div>

                {/* Filters Section */}
                <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
                    <div className="flex gap-4">
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold text-gray-500 uppercase">Geo:</span>
                            <select value={selectedGeo} onChange={(e) => setSelectedGeo(e.target.value)} className="text-sm border-none bg-transparent font-medium text-blue-600 focus:ring-0">
                                <option>All Geographies</option>
                                <option>MEA</option>
                                <option>India</option>
                                <option>ASEAN</option>
                            </select>
                        </div>
                        <div className="flex items-center gap-2 border-l pl-4">
                            <span className="text-xs font-semibold text-gray-500 uppercase">Practice:</span>
                            <select value={selectedPractice} onChange={(e) => setSelectedPractice(e.target.value)} className="text-sm border-none bg-transparent font-medium text-blue-600 focus:ring-0">
                                <option>All Practices</option>
                                <option>MSSP -Cybersecurity</option>
                                <option>ICTM -Cybersecurity</option>
                                <option>TVM -Cybersecurity</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Table Section */}
                <div className="flex-1 overflow-auto bg-white">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-[#F8F9FA] sticky top-0 z-10">
                            <tr>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Win (%)</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Opp ID</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Name</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Owner</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Practice</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Customer</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Sales Stage</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">SA</th>
                                <th className="px-4 py-3 text-left text-[11px] font-bold text-gray-500 uppercase tracking-wider">Est. Billing</th>
                                <th className="px-4 py-3 text-right text-[11px] font-bold text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-100">
                            {loading ? (
                                <tr><td colSpan={10} className="px-6 py-12 text-center text-gray-400 italic">Synchronizing with Oracle CRM...</td></tr>
                            ) : opportunities.length === 0 ? (
                                <tr><td colSpan={10} className="px-6 py-12 text-center text-gray-400 italic">No opportunities found.</td></tr>
                            ) : (
                                opportunities.map((opp) => (
                                    <tr key={opp.id} className="hover:bg-blue-50/30 transition-colors group">
                                        <td className="px-4 py-3 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <span className={`w-8 h-5 flex items-center justify-center rounded text-[10px] font-bold ${(opp.win_probability || 0) >= 70 ? 'bg-green-100 text-green-700' :
                                                        (opp.win_probability || 0) >= 40 ? 'bg-yellow-100 text-yellow-700' :
                                                            'bg-red-100 text-red-700'
                                                    }`}>
                                                    {opp.win_probability || 0}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-xs font-medium text-gray-500">
                                            {opp.remote_id}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div
                                                onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                className="text-xs font-semibold text-blue-600 hover:underline cursor-pointer"
                                            >
                                                {opp.name}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-600">
                                            {opp.sales_owner}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-600">
                                            <span className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-500">{opp.practice || 'MSSP'}</span>
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-700 font-medium">
                                            {opp.customer}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-600">
                                            {opp.stage}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-600">
                                            {opp.assigned_sa || <span className="text-gray-300 italic">Unassigned</span>}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-600">
                                            {opp.estimated_billing_date || 'TBD'}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-right">
                                            <ActionColumn
                                                role={currentUser.role}
                                                opportunity={opp}
                                                onAction={handleAction}
                                            />
                                        </td>
                                    </tr>
                                ))
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
