import React, { useState, useEffect } from 'react';
import { X, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface ApprovalModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (comment: string) => void;
    type: 'APPROVE' | 'REJECT';
    title?: string;
    description?: string;
    isProcessing?: boolean;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    type,
    title,
    description,
    isProcessing = false
}) => {
    const [comment, setComment] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            setComment('');
            setError('');
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSubmit = () => {
        if (type === 'REJECT' && comment.trim().length < 5) {
            setError('Please provide a rejection reason (min 5 chars).');
            return;
        }
        onConfirm(comment);
    };

    const isApprove = type === 'APPROVE';

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md transform transition-all scale-100 p-0 overflow-hidden">
                {/* Header */}
                <div className={`px-6 py-4 flex justify-between items-center border-b ${isApprove ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                    <div className="flex items-center gap-3">
                        {isApprove ? (
                            <div className="p-2 bg-green-100 rounded-full text-green-600">
                                <CheckCircle size={20} />
                            </div>
                        ) : (
                            <div className="p-2 bg-red-100 rounded-full text-red-600">
                                <XCircle size={20} />
                            </div>
                        )}
                        <h3 className={`text-lg font-bold ${isApprove ? 'text-green-800' : 'text-red-800'}`}>
                            {title || (isApprove ? 'Approve Opportunity' : 'Reject Opportunity')}
                        </h3>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6">
                    <p className="text-gray-600 mb-4 text-sm">
                        {description || (isApprove
                            ? "Are you sure you want to approve this opportunity? This will move it to the next stage."
                            : "Please provide a reason for rejecting this opportunity. This will be recorded in the history.")}
                    </p>

                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                            {isApprove ? "Comments (Optional)" : "Rejection Reason (Required)"}
                        </label>
                        <textarea
                            className={`w-full border rounded-lg p-3 text-sm focus:ring-2 focus:outline-none min-h-[100px] resize-none ${error ? 'border-red-300 focus:ring-red-200' :
                                    isApprove ? 'border-gray-300 focus:ring-green-100 focus:border-green-400' :
                                        'border-gray-300 focus:ring-red-100 focus:border-red-400'
                                }`}
                            placeholder={isApprove ? "Add any optional notes..." : "Enter reason for rejection..."}
                            value={comment}
                            onChange={(e) => {
                                setComment(e.target.value);
                                if (error) setError('');
                            }}
                        />
                        {error && (
                            <div className="flex items-center gap-1 text-red-500 text-xs mt-1">
                                <AlertTriangle size={12} />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t border-gray-100">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        disabled={isProcessing}
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isProcessing}
                        className={`px-4 py-2 text-sm font-bold text-white rounded-lg shadow-sm transition-all flex items-center gap-2 ${isApprove
                                ? 'bg-[#217346] hover:bg-[#1a5c38] active:bg-[#14452a]'
                                : 'bg-[#D32F2F] hover:bg-[#b71c1c] active:bg-[#9a1010]'
                            } ${isProcessing ? 'opacity-70 cursor-wait' : ''}`}
                    >
                        {isProcessing ? 'Processing...' : (isApprove ? 'Confirm Approval' : 'Confirm Rejection')}
                    </button>
                </div>
            </div>
        </div>
    );
};
