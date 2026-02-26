import { API_URL } from '../config';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import { AssignSAModal } from '../components/AssignSAModal';
import { useNavigate } from 'react-router-dom';

export const OpportunityInbox: React.FC = () => {
    const { currentUser } = useUser();
    const navigate = useNavigate();
    const [opps, setOpps] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Assign Modal
    const [isAssignModalOpen, setAssignModalOpen] = useState(false);
    const [selectedOpp, setSelectedOpp] = useState<any>(null);

    const fetchOpportunities = async () => {
        if (!currentUser) return;
        setIsLoading(true);
        try {
            const isLead = currentUser.roles.includes("SALES_LEAD");
            const endpoint = isLead ? "unassigned" : "my-assignments";
            const url = ``${API_URL}`/inbox/${endpoint}${!isLead ? `?user_id=${currentUser.user_id}` : ''}`;

            const res = await axios.get(url);
            setOpps(res.data);
        } catch (e) {
            console.error(e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchOpportunities();
    }, [currentUser]);

    const handleAssignClick = (opp: any) => {
        setSelectedOpp(opp);
        setAssignModalOpen(true);
    };

    const isLead = currentUser?.roles.includes("SALES_LEAD");

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">{isLead ? "Unassigned Opportunities" : "My Assignments"}</h1>
            <button onClick={fetchOpportunities} className="mb-4 px-4 py-2 bg-blue-50 text-blue-600 rounded">Refresh</button>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="p-4">Opportunity</th>
                            <th className="p-4">Customer</th>
                            <th className="p-4">Values</th>
                            <th className="p-4">Stage</th>
                            <th className="p-4">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {opps.map(o => (
                            <tr key={o.opp_id} className="hover:bg-gray-50">
                                <td className="p-4">
                                    <div className="font-medium text-blue-600">{o.opp_name}</div>
                                    <div className="text-xs text-gray-500">{o.opp_number}</div>
                                </td>
                                <td className="p-4">{o.customer_name}</td>
                                <td className="p-4 text-sm">
                                    {o.deal_value?.toLocaleString()} {o.currency}
                                </td>
                                <td className="p-4 text-sm text-gray-500">
                                    {new Date(o.crm_last_updated_at).toLocaleDateString()}
                                </td>
                                <td className="p-4">
                                    {isLead ? (
                                        <button
                                            onClick={() => handleAssignClick(o)}
                                            className="px-3 py-1 bg-green-100 text-green-700 rounded text-sm font-medium hover:bg-green-200"
                                        >
                                            Assign SA
                                        </button>
                                    ) : (
                                        <button
                                            onClick={() => navigate(`/score/${o.opp_id}`)}
                                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700"
                                        >
                                            {o.latest_score_status === 'NOT_STARTED' ? 'Score Now' : 'View Score'}
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {opps.length === 0 && (
                            <tr><td colSpan={5} className="p-8 text-center text-gray-500">No opportunities found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>

            {isAssignModalOpen && selectedOpp && (
                <AssignSAModal
                    isOpen={isAssignModalOpen}
                    onClose={() => { setAssignModalOpen(false); fetchOpportunities(); }}
                    opp={selectedOpp}
                />
            )}
        </div>
    );
};
