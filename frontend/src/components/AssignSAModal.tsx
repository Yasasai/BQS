import { API_URL } from '../config';

import React, { useState } from 'react';
import axios from 'axios';
import { useUser } from '../context/UserContext';

export const AssignSAModal = ({ isOpen, onClose, opp }: { isOpen: boolean, onClose: () => void, opp: any }) => {
    const { availableUsers, currentUser } = useUser();
    const [selectedSA, setSelectedSA] = useState("");

    if (!isOpen) return null;

    // Filter only SAs
    const sas = availableUsers.filter(u => u.roles.includes("SA"));

    const handleAssign = async () => {
        if (!selectedSA) return;
        try {
            await axios.post(``${API_URL}`/inbox/assign?opp_id=${opp.opp_id}&assigned_to_user_id=${selectedSA}&assigned_by_user_id=${currentUser?.user_id}`);
            onClose();
        } catch (e) {
            alert("Assignment Failed");
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h3 className="text-lg font-bold mb-4">Assign Solution Architect</h3>
                <p className="mb-4 text-sm text-gray-600">Assigning <strong>{opp.opp_name}</strong></p>

                <label className="block text-sm font-medium mb-1">Select SA</label>
                <select
                    className="w-full border p-2 rounded mb-6"
                    value={selectedSA}
                    onChange={(e) => setSelectedSA(e.target.value)}
                >
                    <option value="">-- Select --</option>
                    {sas.map(u => <option key={u.user_id} value={u.user_id}>{u.display_name}</option>)}
                </select>

                <div className="flex justify-end gap-2">
                    <button onClick={onClose} className="px-4 py-2 bg-gray-200 rounded">Cancel</button>
                    <button onClick={handleAssign} className="px-4 py-2 bg-blue-600 text-white rounded">Confirm Assignment</button>
                </div>
            </div>
        </div>
    );
};
