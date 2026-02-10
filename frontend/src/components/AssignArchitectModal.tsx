import React, { useState, useEffect } from 'react';
import { X, User, Shield, Info } from 'lucide-react';

export interface AssignmentData {
    sa_owner: string;  // This will be the email/ID
    secondary_sa?: string;
    priority: 'High' | 'Medium' | 'Low';
    notes?: string;
}

interface AssignArchitectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAssign: (data: AssignmentData) => void;
    opportunityIds: (number | string)[]; // Support string IDs
    targetRole?: string; // SA, PH, SH, SP
    title?: string;
}

interface User {
    user_id: string;
    display_name: string;
    email: string;
    roles: string[];
}

export const AssignArchitectModal: React.FC<AssignArchitectModalProps> = ({
    isOpen,
    onClose,
    onAssign,
    opportunityIds,
    targetRole = 'SA',
    title = 'Assign Solution Architect'
}) => {
    const [selectedUser, setSelectedUser] = useState('');
    const [secondaryUser, setSecondaryUser] = useState('');
    const [priority, setPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
    const [notes, setNotes] = useState('');
    const [availableUsers, setAvailableUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);

    // Fetch Users from database
    useEffect(() => {
        if (isOpen) {
            setLoading(true);
            // Fetch users with specific role
            fetch(`http://127.0.0.1:8000/api/auth/users?role=${targetRole}`)
                .then(res => res.json())
                .then((users: User[]) => {
                    setAvailableUsers(users);
                    setLoading(false);
                })
                .catch(err => {
                    console.error('Failed to load users:', err);
                    setLoading(false);
                });
        }
    }, [isOpen, targetRole]);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedUser) return;

        // Find the user object to send ID if needed, but keeping email/ID interface for now
        // The parent component handles the API call which likely expects user_id
        // Changed: We pass user_id if possible, but let's see how onAssign is used.
        // Existing usage passes 'email' or string.
        // Let's pass user_id if available, or selected value.

        onAssign({
            sa_owner: selectedUser,
            secondary_sa: secondaryUser,
            priority,
            notes
        });

        // Reset and close
        setSelectedUser('');
        setSecondaryUser('');
        setPriority('Medium');
        setNotes('');
        onClose();
    };

    console.log('🟢 AssignArchitectModal render:', { isOpen, targetRole, opportunityIds });

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-purple-100 text-purple-600 rounded-lg">
                            <Shield size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900 leading-tight">{title}</h2>
                            <p className="text-xs text-gray-500 mt-0.5">Assigning {opportunityIds.length} item(s)</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-white rounded-lg transition-colors text-gray-400 hover:text-gray-600 border border-transparent hover:border-gray-200"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="p-6 space-y-5">
                        {/* Primary Selection */}
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                                <User size={12} /> Primary Assignee
                            </label>
                            <select
                                required
                                value={selectedUser}
                                onChange={(e) => setSelectedUser(e.target.value)}
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-500/10 focus:border-purple-500 outline-none transition-all"
                                disabled={loading}
                            >
                                <option value="">{loading ? 'Loading...' : 'Select User...'}</option>
                                {availableUsers.map(u => (
                                    <option key={u.user_id} value={u.user_id}>{u.display_name} ({u.email})</option>
                                ))}
                            </select>
                        </div>

                        {/* Secondary Selection (Only for SA really, but keeping it) */}
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                                Secondary (Optional)
                            </label>
                            <select
                                value={secondaryUser}
                                onChange={(e) => setSecondaryUser(e.target.value)}
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-500/10 focus:border-purple-500 outline-none transition-all"
                                disabled={loading}
                            >
                                <option value="">None</option>
                                {availableUsers.filter(u => u.user_id !== selectedUser).map(u => (
                                    <option key={u.user_id} value={u.user_id}>{u.display_name} ({u.email})</option>
                                ))}
                            </select>
                        </div>

                        {/* Priority & Notes */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">Priority</label>
                                <div className="flex gap-2">
                                    {(['Low', 'Medium', 'High'] as const).map(p => (
                                        <button
                                            key={p}
                                            type="button"
                                            onClick={() => setPriority(p)}
                                            className={`flex-1 py-2 text-xs font-bold rounded-lg border transition-all ${priority === p
                                                ? 'bg-purple-50 border-purple-200 text-purple-700 ring-2 ring-purple-500/5'
                                                : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                                                }`}
                                        >
                                            {p}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">Internal Deadline</label>
                                <input
                                    type="date"
                                    className="w-full px-4 py-2 bg-gray-50 border border-gray-100 rounded-lg text-xs font-medium text-gray-600"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                                <Info size={12} /> Instructions
                            </label>
                            <textarea
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                placeholder="Add specific guidance or context..."
                                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm h-24 focus:ring-2 focus:ring-purple-500/10 focus:border-purple-500 outline-none transition-all resize-none"
                            />
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2.5 text-sm font-semibold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={!selectedUser}
                            className={`flex-1 px-4 py-2.5 text-sm font-bold text-white rounded-lg shadow-sm transition-all ${!selectedUser
                                ? 'bg-purple-300 cursor-not-allowed'
                                : 'bg-purple-600 hover:bg-purple-700 hover:shadow-md active:scale-[0.98]'
                                }`}
                        >
                            Confirm Allocation
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
