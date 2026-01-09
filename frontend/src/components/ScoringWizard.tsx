import React, { useState } from 'react';
import { Opportunity } from '../types';
import { ChevronLeft, ChevronRight, Save, Send, AlertTriangle } from 'lucide-react';

interface Props {
    opportunity: Opportunity;
    onClose: () => void;
    onSuccess: () => void;
}

const QUESTIONS = [
    { id: 'q1', text: 'Does the deal exceed $500k in net revenue?', category: 'Commercial' },
    { id: 'q2', text: 'Are resources available in the required timeframe?', category: 'Feasibility' },
    { id: 'q3', text: 'Is this a strategic account for the practice?', category: 'Strategic' },
    { id: 'q4', text: 'Do we have a pre-existing relationship with the CIO?', category: 'Relationship' },
];

export const ScoringWizard: React.FC<Props> = ({ opportunity, onClose, onSuccess }) => {
    const [step, setStep] = useState(0);
    const [scores, setScores] = useState<Record<string, number>>({});
    const [notes, setNotes] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleScore = (val: number) => {
        setScores({ ...scores, [QUESTIONS[step].id]: val });
        if (step < QUESTIONS.length - 1) setStep(step + 1);
    };

    const calculateFinalScore = () => {
        const vals = Object.values(scores);
        if (vals.length === 0) return 0;
        return (vals.reduce((a, b) => a + b, 0) / (QUESTIONS.length * 10)) * 100;
    };

    const handleFinalSubmit = async (isDraft: boolean) => {
        setIsSubmitting(true);
        const finalScore = calculateFinalScore();

        try {
            const response = await fetch(`http://localhost:8000/api/opportunities/${opportunity.id}/submit-assessment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    score: finalScore,
                    notes: notes,
                    is_draft: isDraft
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
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-gray-900/40 backdrop-blur-sm">
            <div className="bg-white w-full max-w-2xl h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
                <div className="p-8 border-b border-gray-100 flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-[10px] font-bold uppercase tracking-wider rounded">Step {step + 1} of {QUESTIONS.length}</span>
                            <h2 className="text-xl font-bold text-gray-900">Bid Qualification</h2>
                        </div>
                        <p className="text-sm text-gray-500">Assessing: {opportunity.name}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-50 rounded-full transition-colors">
                        <ChevronLeft size={24} className="text-gray-400" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-12">
                    <div className="max-w-md mx-auto space-y-12">
                        <div className="space-y-4">
                            <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-[0.2em]">{QUESTIONS[step].category}</p>
                            <h3 className="text-2xl font-semibold text-gray-800 leading-snug">{QUESTIONS[step].text}</h3>

                            <div className="grid grid-cols-5 gap-3 pt-6">
                                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((v) => (
                                    <button
                                        key={v}
                                        onClick={() => handleScore(v)}
                                        className={`h-12 rounded-xl border-2 font-bold text-sm transition-all ${scores[QUESTIONS[step].id] === v
                                                ? 'border-indigo-600 bg-indigo-50 text-indigo-700 shadow-lg ring-4 ring-indigo-500/10'
                                                : 'border-gray-100 bg-white text-gray-400 hover:border-indigo-200 hover:text-indigo-500'
                                            }`}
                                    >
                                        {v}
                                    </button>
                                ))}
                            </div>
                            <div className="flex justify-between text-[10px] font-bold text-gray-300 uppercase mt-2">
                                <span>Low Probability</span>
                                <span>Highly Qualified</span>
                            </div>
                        </div>

                        {step === QUESTIONS.length - 1 && (
                            <div className="pt-12 border-t border-gray-100 space-y-6 animate-in fade-in slide-in-from-bottom-4">
                                <div className="space-y-3">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Architect's Justification</label>
                                    <textarea
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        placeholder="Provide technical justification for the scoring above..."
                                        className="w-full h-32 p-4 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none bg-gray-50/30"
                                    />
                                </div>

                                <div className="p-4 bg-amber-50 rounded-xl flex gap-3 border border-amber-100">
                                    <AlertTriangle className="text-amber-500 shrink-0" size={18} />
                                    <p className="text-xs text-amber-700 leading-relaxed font-medium">Finalizing submission will transition this deal to Practice Review. You will not be able to edit scores after submission.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-8 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
                    <div className="flex gap-2">
                        <button
                            onClick={() => step > 0 && setStep(step - 1)}
                            className="px-6 py-3 text-sm font-bold text-gray-500 hover:text-gray-800 transition-colors"
                        >
                            Previous
                        </button>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={() => handleFinalSubmit(true)}
                            className="px-5 py-3 text-sm font-bold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-100 transition-all flex items-center gap-2 shadow-sm"
                        >
                            <Save size={16} /> Save Draft
                        </button>
                        <button
                            onClick={() => handleFinalSubmit(false)}
                            disabled={Object.keys(scores).length < QUESTIONS.length || isSubmitting}
                            className={`px-8 py-3 text-sm font-black text-white rounded-xl shadow-lg transition-all flex items-center gap-2 ${Object.keys(scores).length < QUESTIONS.length || isSubmitting
                                    ? 'bg-indigo-300 cursor-not-allowed'
                                    : 'bg-indigo-600 hover:bg-indigo-700 hover:-translate-y-0.5 active:translate-y-0'
                                }`}
                        >
                            <Send size={16} /> {isSubmitting ? 'Submitting...' : 'Final Submission'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
