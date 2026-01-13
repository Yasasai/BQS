import React from 'react';
import { Opportunity } from '../types';
import { MoreHorizontal, Play, CheckCircle, UserPlus, FileText, Send } from 'lucide-react';

interface ActionColumnProps {
    role: 'MANAGEMENT' | 'PRACTICE_HEAD' | 'SOLUTION_ARCHITECT';
    opportunity: Opportunity;
    onAction: (action: string, opp: Opportunity) => void;
}

export const ActionColumn: React.FC<ActionColumnProps> = ({ role, opportunity, onAction }) => {
    const status = opportunity.status || 'New from CRM';

    const renderManagementActions = () => {
        if (status === 'High Value / Governance Needed') {
            return (
                <div className="flex gap-2">
                    <button
                        onClick={() => onAction('FINAL_APPROVE', opportunity)}
                        className="px-3 py-1.5 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium text-xs transition-colors"
                    >
                        Final Approve
                    </button>
                    <button
                        onClick={() => onAction('DROP_BID', opportunity)}
                        className="px-3 py-1.5 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium text-xs transition-colors"
                    >
                        Drop Bid
                    </button>
                </div>
            );
        }
        return <span className="text-gray-400 text-xs italic">Reviewing...</span>;
    };

    const renderPracticeHeadActions = () => {
        if (status === 'New from CRM') {
            return (
                <button
                    onClick={() => onAction('ASSIGN_TO_SA', opportunity)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-xs transition-colors"
                >
                    <UserPlus size={14} /> Assign to SA
                </button>
            );
        }
        if (status === 'Scoring Pending') {
            return <span className="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-md font-medium text-xs">Waiting for SA</span>;
        }
        if (status === 'Scored by SA') {
            return (
                <div className="flex gap-2">
                    <button
                        onClick={() => onAction('APPROVE_FOR_BID', opportunity)}
                        className="px-3 py-1.5 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium text-xs transition-colors"
                    >
                        Approve for Bid
                    </button>
                    <button
                        onClick={() => onAction('REJECT', opportunity)}
                        className="px-3 py-1.5 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium text-xs transition-colors"
                    >
                        Reject
                    </button>
                </div>
            );
        }
        return <span className="text-gray-400 text-xs italic">In Progress</span>;
    };

    const renderSAActions = () => {
        if (status === 'Assigned') {
            return (
                <button
                    onClick={() => onAction('START_ASSESSMENT', opportunity)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 font-medium text-xs transition-colors"
                >
                    <Play size={14} /> Start Assessment
                </button>
            );
        }
        if (status === 'Draft') {
            return (
                <div className="flex gap-2">
                    <button
                        onClick={() => onAction('SAVE_DRAFT', opportunity)}
                        className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium text-xs transition-colors"
                    >
                        Save Draft
                    </button>
                    <button
                        onClick={() => onAction('SUBMIT_SCORE', opportunity)}
                        className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium text-xs transition-colors"
                    >
                        Submit Score
                    </button>
                </div>
            );
        }
        return <span className="text-gray-400 text-xs italic">Submitted</span>;
    };

    return (
        <div className="flex justify-end">
            {role === 'MANAGEMENT' && renderManagementActions()}
            {role === 'PRACTICE_HEAD' && renderPracticeHeadActions()}
            {role === 'SOLUTION_ARCHITECT' && renderSAActions()}
        </div>
    );
};
