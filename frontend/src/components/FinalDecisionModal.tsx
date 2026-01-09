import React, { useState } from 'react';
import { Opportunity } from '../types';
import { X, CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';

interface Props {
    opportunity: Opportunity;
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export const FinalDecisionModal: React.FC<Props> = ({ opportunity, isOpen, onClose, onSuccess }) => {
    const [comments, setComments] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!isOpen) return null;

    const handleDecision = async (decision: 'GO' | 'NO_GO') => {
        if (decision === 'NO_GO' && !comments) {
            alert('Please provide a reason for the No-Bid decision.');
            return;
        }

        setIsSubmitting(true);
        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${opportunity.id}/final-decision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    decision,
                    comments,
                    final_score: opportunity.win_probability
                }),
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
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="px-8 py-5 flex items-center justify-between border-b border-gray-100 bg-gray-50/50">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 leading-tight">Final Governance Decision</h2>
                        <p className="text-sm text-gray-500 mt-0.5">{opportunity.name} • {opportunity.remote_id}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white rounded-lg transition-colors text-gray-400 hover:text-gray-600 border border-transparent hover:border-gray-200">
                        <X size={20} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-5 bg-blue-50/50 rounded-xl border border-blue-100">
                            <label className="text-[10px] font-bold text-blue-500 uppercase tracking-widest block mb-2">Technical Score</label>
                            <div className="flex items-baseline gap-2">
                                <span className="text-3xl font-black text-blue-700">{Math.round(opportunity.win_probability || 0)}%</span>
                                <span className="text-xs font-semibold text-blue-500">Win Probability</span>
                            </div>
                        </div>
                        <div className="p-5 bg-purple-50/50 rounded-xl border border-purple-100">
                            <label className="text-[10px] font-bold text-purple-500 uppercase tracking-widest block mb-2">Deal Health</label>
                            <div className="flex items-center gap-2">
                                <CheckCircle size={18} className="text-purple-600" />
                                <span className="text-sm font-bold text-purple-700">Practice Approved</span>
                            </div>
                        </div>
                    </div>

                    {/* SA Notes Section */}
                    <div className="space-y-3">
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                            <FileText size={14} /> Solution Architect's Summary
                        </label>
                        <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 italic text-sm text-gray-600 leading-relaxed shadow-sm">
                            "{opportunity.practice_head_comments || 'High quality technical fit. Resource mapping complete for Q3 execution.'}"
                        </div>
                    </div>

                    {/* Decision Inputs */}
                    <div className="space-y-4">
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block">Governance Comments / Close Reason</label>
                        <textarea
                            value={comments}
                            onChange={(e) => setComments(e.target.value)}
                            placeholder="Enter final decision notes or rejection reasons..."
                            className="w-full h-32 p-4 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none bg-white shadow-sm"
                        />
                    </div>

                    <div className="p-4 bg-amber-50 rounded-xl flex gap-3 border border-amber-100">
                        <AlertCircle className="text-amber-500 shrink-0" size={18} />
                        <p className="text-xs text-amber-700 leading-relaxed">
                            <strong>GO Decision</strong> will sync this status back to the CRM and trigger the contract phase.
                            <strong>NO-GO Decision</strong> will close this opportunity.
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-8 py-6 bg-gray-50 border-t border-gray-100 flex gap-4">
                    <button
                        disabled={isSubmitting}
                        onClick={() => handleDecision('NO_GO')}
                        className="flex-1 px-6 py-3.5 text-sm font-bold text-red-600 bg-white border border-red-200 rounded-xl hover:bg-red-50 transition-all flex items-center justify-center gap-2 shadow-sm"
                    >
                        <XCircle size={18} /> Reject (NO-GO)
                    </button>
                    <button
                        disabled={isSubmitting}
                        onClick={() => handleDecision('GO')}
                        className="flex-3 px-12 py-3.5 text-sm font-black text-white bg-blue-600 rounded-xl shadow-lg hover:bg-blue-700 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2"
                    >
                        <CheckCircle size={18} /> {isSubmitting ? 'Processing...' : 'Approve (GO)'}
                    </button>
                </div>
            </div>
        </div>
    );
};
