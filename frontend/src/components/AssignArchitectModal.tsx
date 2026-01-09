import React, { useState } from 'react';
import { X, User, Shield, Info } from 'lucide-react';

export interface AssignmentData {
    sa_owner: string;
    secondary_sa?: string;
    priority: 'High' | 'Medium' | 'Low';
    notes?: string;
}

interface AssignArchitectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAssign: (data: AssignmentData) => void;
    opportunityIds: number[];
}

const SOLUTION_ARCHITECTS = [
    { id: '1', name: 'Jane Smith', expertise: 'Cloud Infrastructure' },
    { id: '2', name: 'Michael Chen', expertise: 'Cybersecurity' },
    { id: '3', name: 'Sarah Johnson', expertise: 'Data Analytics' },
    { id: '4', name: 'Robert Wilson', expertise: 'AI & ML' },
    { id: '5', name: 'Emily Davis', expertise: 'Digital Transformation' }
];

export const AssignArchitectModal: React.FC<AssignArchitectModalProps> = ({
    isOpen,
    onClose,
    onAssign,
    opportunityIds
}) => {
    const [selectedSA, setSelectedSA] = useState('');
    const [secondarySA, setSecondarySA] = useState('');
    const [priority, setPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
    const [notes, setNotes] = useState('');

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedSA) return;

        onAssign({
            sa_owner: selectedSA,
            secondary_sa: secondarySA,
            priority,
            notes
        });

        // Reset and close
        setSelectedSA('');
        setSecondarySA('');
        setPriority('Medium');
        setNotes('');
        onClose();
    };

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
                            <h2 className="text-lg font-bold text-gray-900 leading-tight">Assign Solution Architect</h2>
                            <p className="text-xs text-gray-500 mt-0.5">Assigning {opportunityIds.length} deals to technical owner</p>
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
                        {/* Primary SA Selection */}
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                                <User size={12} /> Primary Solution Architect
                            </label>
                            <select
                                required
                                value={selectedSA}
                                onChange={(e) => setSelectedSA(e.target.value)}
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-500/10 focus:border-purple-500 outline-none transition-all"
                            >
                                <option value="">Select an Architect...</option>
                                {SOLUTION_ARCHITECTS.map(sa => (
                                    <option key={sa.id} value={sa.name}>{sa.name} ({sa.expertise})</option>
                                ))}
                            </select>
                        </div>

                        {/* Secondary SA Selection */}
                        <div className="space-y-2">
                            <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
                                Secondary / Peer Reviewer (Optional)
                            </label>
                            <select
                                value={secondarySA}
                                onChange={(e) => setSecondarySA(e.target.value)}
                                className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-500/10 focus:border-purple-500 outline-none transition-all"
                            >
                                <option value="">None</option>
                                {SOLUTION_ARCHITECTS.filter(sa => sa.name !== selectedSA).map(sa => (
                                    <option key={sa.id} value={sa.name}>{sa.name} ({sa.expertise})</option>
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
                                <Info size={12} /> Architect Instructions
                            </label>
                            <textarea
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                placeholder="Add specific guidance or context for the assessment..."
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
                            disabled={!selectedSA}
                            className={`flex-1 px-4 py-2.5 text-sm font-bold text-white rounded-lg shadow-sm transition-all ${!selectedSA
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
