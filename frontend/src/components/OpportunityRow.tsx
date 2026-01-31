import React from 'react';
import { Opportunity } from '../types';
import { CheckCircle, XCircle, Link as LinkIcon, UserPlus } from 'lucide-react';

interface OpportunityRowProps {
    opp: Opportunity;
    onAssign: (opp: Opportunity) => void;
    onApprove: (id: number) => void;
    onReject: (id: number) => void;
    onView: (id: number) => void;
    formatCurrency: (val: number) => string;
}

export const OpportunityRow: React.FC<OpportunityRowProps> = ({
    opp,
    onAssign,
    onApprove,
    onReject,
    onView,
    formatCurrency
}) => {
    return (
        <tr
            className="hover:bg-gray-50 transition-colors group cursor-pointer text-[12px] border-b border-gray-100"
            onClick={() => onView(opp.id)}
        >
            <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                <input type="checkbox" className="w-3.5 h-3.5 rounded border-gray-300 text-[#0572CE] focus:ring-[#0572CE]" />
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
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-normal ${['Committed', 'Won', 'APPROVED', 'ACCEPTED'].includes(opp.workflow_status || '')
                        ? 'bg-[#E8F5E9] text-[#2E7D32]'
                        : (opp.workflow_status === 'SUBMITTED_FOR_REVIEW' || opp.workflow_status === 'SUBMITTED')
                            ? 'bg-amber-50 text-amber-700'
                            : 'bg-gray-100 text-gray-600'
                    }`}>
                    {opp.workflow_status?.replace(/_/g, ' ') || 'Open'}
                </span>
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
                {/* Assign Button */}
                {(opp.workflow_status === 'NEW' || !opp.workflow_status || opp.workflow_status === 'OPEN') && (
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onAssign(opp);
                        }}
                        className="text-[11px] bg-[#0572CE] text-white px-3 py-1 rounded hover:bg-[#005a9e] transition-colors"
                    >
                        Assign
                    </button>
                )}

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

                {/* View Actions */}
                {['APPROVED', 'ACCEPTED', 'REJECTED', 'COMPLETED', 'WON', 'LOST'].includes(opp.workflow_status || '') ? (
                    <button onClick={(e) => {
                        e.stopPropagation();
                        onView(opp.id);
                    }} className="text-[11px] font-bold text-gray-400 hover:text-gray-600 uppercase">
                        View
                    </button>
                ) : opp.workflow_status === 'ASSIGNED_TO_SA' ? (
                    <button onClick={(e) => {
                        e.stopPropagation();
                        onAssign(opp);
                    }} className="text-[11px] text-gray-400 hover:text-[#0572CE]">Reassign</button>
                ) : null}
            </td>
        </tr>
    );
};
