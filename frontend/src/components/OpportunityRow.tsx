import React from 'react';
import { Opportunity } from '../types';
import { CheckCircle, XCircle, Link as LinkIcon, UserPlus } from 'lucide-react';

interface OpportunityRowProps {
    opp: Opportunity;
    onAssign: (opp: Opportunity) => void;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
    onView: (id: string, jumpToScore?: boolean) => void;
    formatCurrency: (val: number) => string;
    selected: boolean;
    onSelect: (id: string, checked: boolean) => void;
}

export const OpportunityRow: React.FC<OpportunityRowProps> = ({
    opp,
    onAssign,
    onApprove,
    onReject,
    onView,
    formatCurrency,
    selected,
    onSelect
}) => {
    return (
        <tr
            className="hover:bg-gray-50 transition-colors group cursor-pointer text-[12px] border-b border-gray-100"
            onClick={() => onView(opp.id)}
        >
            <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                <input
                    type="checkbox"
                    className="w-3.5 h-3.5 rounded border-gray-300 text-[#0572CE] focus:ring-[#0572CE]"
                    checked={selected}
                    onChange={(e) => onSelect(opp.id, e.target.checked)}
                />
            </td>
            <td className="px-2 py-3">
                <span className="inline-flex items-center justify-center w-8 h-5 rounded-full text-[11px] font-bold bg-[#FFE57F] text-[#333333]">
                    {opp.win_probability || 0}
                </span>
            </td>
            <td className="px-2 py-3 text-[#333333] font-normal">
                {opp.remote_id}
            </td>
            <td className="px-2 py-3 text-[#0572ce] font-normal hover:underline cursor-pointer">
                {opp.name}
            </td>
            <td className="px-2 py-3 text-[#333333]">
                {opp.sales_owner || '-'}
            </td>
            <td className="px-2 py-3 text-[#333333]">
                {opp.practice || '-'}
            </td>
            <td className="px-2 py-3">
                {(() => {
                    const status = (opp.workflow_status || 'NEW').toUpperCase();
                    let styles = 'bg-gray-100 text-gray-600';
                    let label = status.replace(/_/g, ' ');

                    if (['NEW', 'OPEN'].includes(status)) {
                        styles = 'bg-slate-100 text-slate-600 border border-slate-200';
                        label = 'New';
                    } else if (status === 'ASSIGNED_TO_SA') {
                        styles = 'bg-blue-50 text-blue-700 border border-blue-100';
                        label = 'Assigned';
                    } else if (status === 'UNDER_ASSESSMENT') {
                        styles = 'bg-indigo-50 text-indigo-700 border border-indigo-100';
                        label = 'Assessment';
                    } else if (['SUBMITTED', 'SUBMITTED_FOR_REVIEW'].includes(status)) {
                        styles = 'bg-amber-50 text-amber-700 border border-amber-200';
                        label = 'Review Required';
                    } else if (['APPROVED', 'ACCEPTED', 'WON', 'COMPLETED'].includes(status)) {
                        styles = 'bg-emerald-50 text-emerald-700 border border-emerald-200';
                        label = 'Approved';
                    } else if (['REJECTED', 'LOST'].includes(status)) {
                        styles = 'bg-rose-50 text-rose-700 border border-rose-200';
                        label = 'Rejected';
                    }

                    return (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${styles}`}>
                            {label}
                        </span>
                    );
                })()}
            </td>
            <td className="px-2 py-3">
                <div className="flex items-center gap-1.5">
                    {opp.assigned_sa ? (
                        <>
                            <div className="w-5 h-5 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
                                <UserPlus size={10} className="text-[#0572CE]" />
                            </div>
                            <span className="text-[#0572CE] font-semibold">{opp.assigned_sa}</span>
                        </>
                    ) : (
                        <span className="text-gray-300 italic">Unassigned</span>
                    )}
                </div>
            </td>
            <td className="px-2 py-3 text-[#666666]">
                {opp.stage_entered_at ? new Date(opp.stage_entered_at).toLocaleDateString() : '-'}
            </td>
            <td className="px-2 py-3 text-[#333333]">
                {opp.customer}
            </td>
            <td className="px-2 py-3 text-[#999999]">
                -
            </td>
            <td className="px-2 py-3 text-right text-[#333333] font-medium">
                {formatCurrency(opp.deal_value)}
            </td>
            <td className="px-2 py-3 text-[#666666]">
                {opp.estimated_billing_date || '-'}
            </td>
            <td className="px-2 py-3">
                <div className="text-[#333333]">{opp.stage || 'Lead'}</div>
                <div className="text-[10px] text-gray-400">PO Received</div>
            </td>
            <td className="px-2 py-3 text-[#666666]">
                {opp.geo || opp.region || '-'}
            </td>
            <td className="px-2 py-3 text-right whitespace-nowrap">
                {/* Review Actions */}
                {(opp.workflow_status === 'SUBMITTED_FOR_REVIEW' || opp.workflow_status === 'SUBMITTED') && (
                    <div className="flex justify-end gap-2" onClick={e => e.stopPropagation()}>
                        <button
                            onClick={() => onApprove(opp.id)}
                            className="px-2 py-1 text-[11px] font-bold bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] rounded hover:bg-[#C8E6C9] transition-colors flex items-center gap-1"
                        >
                            <CheckCircle size={12} /> Accept
                        </button>
                        <button
                            onClick={() => onReject(opp.id)}
                            className="px-2 py-1 text-[11px] font-bold bg-[#FFEBEE] text-[#C62828] border border-[#FFCDD2] rounded hover:bg-[#FFCDD2] transition-colors flex items-center gap-1"
                        >
                            <XCircle size={12} /> Reject
                        </button>
                    </div>
                )}

                {/* Action Buttons: Unified Review & View */}
                <div className="flex flex-col gap-1 items-end" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-2 mb-1">
                        {opp.version_no !== null && (
                            <button
                                onClick={() => onView(opp.id, true)}
                                className="text-[10px] font-bold text-[#E27D12] hover:text-[#c46a0a] uppercase border border-[#E27D12] px-1.5 py-0.5 rounded transition-colors"
                            >
                                Score
                            </button>
                        )}
                        <button
                            onClick={() => onView(opp.id, false)}
                            className="text-[10px] font-bold text-[#0572CE] hover:text-[#005a9e] uppercase border border-[#0572CE] px-1.5 py-0.5 rounded transition-colors"
                        >
                            View
                        </button>
                    </div>
                </div>
            </td>
        </tr>
    );
};
