import { API_URL } from '../config';
import React, { useState } from 'react';
import { Opportunity } from '../types';
import { X, ChevronRight } from 'lucide-react';

interface Props {
    opportunity: Opportunity;
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const PRACTICES = ['Cloud Infrastructure', 'Cybersecurity', 'AI & Machine Learning', 'Digital Transformation', 'Data Analytics'];

export const AssignPracticeModal: React.FC<Props> = ({ opportunity, isOpen, onClose, onSuccess }) => {
    const [selectedPractice, setSelectedPractice] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async () => {
        if (!selectedPractice) return;
        setIsSubmitting(true);

        try {
            const response = await fetch(``${API_URL}`/opportunities/${opportunity.id}/assign-practice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ practice: selectedPractice }),
            });

            if (response.ok) {
                onSuccess();
                onClose();
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
                <div className="px-6 py-4 flex items-center justify-between border-b border-gray-100 bg-gray-50/50">
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 leading-tight">Assign Practice</h2>
                        <p className="text-xs text-gray-500 mt-0.5">{opportunity.name} • {opportunity.remote_id}</p>
                    </div>
                    <button onClick={onClose} className="p-1.5 hover:bg-white rounded-lg transition-colors text-gray-400 hover:text-gray-600 border border-transparent hover:border-gray-200">
                        <X size={18} />
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    <div className="space-y-2">
                        <label className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">Select Target Practice</label>
                        <div className="grid grid-cols-1 gap-2">
                            {PRACTICES.map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setSelectedPractice(p)}
                                    className={`flex items-center justify-between px-4 py-3 rounded-lg border text-sm font-medium transition-all ${selectedPractice === p
                                            ? 'border-blue-500 bg-blue-50 text-blue-700 ring-2 ring-blue-500/10'
                                            : 'border-gray-200 bg-white text-gray-600 hover:border-blue-200 hover:bg-gray-50'
                                        }`}
                                >
                                    {p}
                                    {selectedPractice === p && <ChevronRight size={14} />}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex gap-3">
                    <button onClick={onClose} className="flex-1 px-4 py-2.5 text-sm font-semibold text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={!selectedPractice || isSubmitting}
                        className={`flex-1 px-4 py-2.5 text-sm font-semibold text-white rounded-lg shadow-sm transition-all focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${!selectedPractice || isSubmitting
                                ? 'bg-blue-300 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'
                            }`}
                    >
                        {isSubmitting ? 'Routing...' : 'Confirm Assignment'}
                    </button>
                </div>
            </div>
        </div>
    );
};
