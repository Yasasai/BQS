import React from 'react';
import { Opportunity } from '../types';
import { MoreHorizontal, Play, CheckCircle, UserPlus, FileText, Send } from 'lucide-react';

interface ActionColumnProps {
    role: 'MANAGEMENT' | 'PRACTICE_HEAD' | 'SA';
    opportunity: Opportunity;
    onAction: (action: string, opp: Opportunity) => void;
}

export const ActionColumn: React.FC<ActionColumnProps> = ({ role, opportunity, onAction }) => {
    const status = opportunity.status;

    const renderManagementActions = () => {
        switch (status) {
            case 'NEW':
                return (
                    <button
                        onClick={() => onAction('ASSIGN_PRACTICE', opportunity)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 font-medium text-xs transition-colors"
                    >
                        <MoreHorizontal size={14} /> Assign Practice
                    </button>
                );
            case 'PENDING_GOVERNANCE':
                return (
                    <button
                        onClick={() => onAction('FINAL_DECISION', opportunity)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-600 rounded-md hover:bg-green-100 font-medium text-xs transition-colors"
                    >
                        <CheckCircle size={14} /> Final Decision
                    </button>
                );
            default:
                return <span className="text-gray-400 text-xs italic">Awaiting Team</span>;
        }
    };

    const renderPracticeHeadActions = () => {
        switch (status) {
            case 'ASSIGNED_TO_PRACTICE':
                return (
                    <button
                        onClick={() => onAction('ASSIGN_ARCHITECT', opportunity)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 text-purple-600 rounded-md hover:bg-purple-100 font-medium text-xs transition-colors"
                    >
                        <UserPlus size={14} /> Assign Architect
                    </button>
                );
            case 'REVIEW_PENDING':
                return (
                    <button
                        onClick={() => onAction('SCORE_REVIEW', opportunity)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 text-orange-600 rounded-md hover:bg-orange-100 font-medium text-xs transition-colors"
                    >
                        <FileText size={14} /> Review Score
                    </button>
                );
            default:
                return <span className="text-gray-400 text-xs italic">Syncing...</span>;
        }
    };

    const renderSAActions = () => {
        if (status === 'PENDING_ASSESSMENT') {
            return (
                <button
                    onClick={() => onAction('START_WIZARD', opportunity)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 rounded-md hover:bg-indigo-100 font-medium text-xs transition-colors"
                >
                    <Play size={14} /> Start Assessment
                </button>
            );
        }
        if (status === 'DRAFT') {
            return (
                <button
                    onClick={() => onAction('CONTINUE_WIZARD', opportunity)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 font-medium text-xs transition-colors"
                >
                    <Send size={14} /> Continue & Submit
                </button>
            );
        }
        return <span className="text-gray-400 text-xs italic">In Process</span>;
    };

    return (
        <div className="flex justify-end">
            {role === 'MANAGEMENT' && renderManagementActions()}
            {role === 'PRACTICE_HEAD' && renderPracticeHeadActions()}
            {role === 'SA' && renderSAActions()}
        </div>
    );
};
