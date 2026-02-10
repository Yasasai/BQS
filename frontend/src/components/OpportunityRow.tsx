import React from 'react';
import { Opportunity } from '../types';
import { CheckCircle, XCircle, Link as LinkIcon, UserPlus } from 'lucide-react';

interface OpportunityRowProps {
    opp: Opportunity;
    onAssign: (opp: Opportunity, type?: 'PH' | 'SH' | 'SA' | 'SP') => void;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
    onView: (id: string, jumpToScore?: boolean) => void;
    formatCurrency: (val: number) => string;
    selected: boolean;
    onSelect: (id: string, checked: boolean) => void;
    role?: 'GH' | 'PH' | 'SH' | 'SA' | 'SP';
}

export const OpportunityRow: React.FC<OpportunityRowProps> = ({
    opp,
    onAssign,
    onApprove,
    onReject,
    onView,
    formatCurrency,
    selected,
    onSelect,
    role = 'GH'
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
                    } else if (status === 'HEADS_ASSIGNED') {
                        styles = 'bg-blue-50 text-blue-700 border border-blue-100';
                        label = 'Heads Assigned';
                    } else if (status === 'EXECUTORS_ASSIGNED') {
                        styles = 'bg-cyan-50 text-cyan-700 border border-cyan-100';
                        label = 'Team Assigned';
                    } else if (status === 'IN_ASSESSMENT') {
                        styles = 'bg-indigo-50 text-indigo-700 border border-indigo-100';
                        label = 'In Progress';
                    } else if (status === 'UNDER_REVIEW') {
                        styles = 'bg-amber-50 text-amber-700 border border-amber-200';
                        label = 'Under Review';
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

            {/* Dynamic Assignment Column */}
            {role === 'PH' && (
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
            )}

            {role === 'SH' && (
                <td className="px-2 py-3">
                    <div className="flex items-center gap-1.5">
                        {opp.assigned_sp ? (
                            <>
                                <div className="w-5 h-5 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
                                    <UserPlus size={10} className="text-purple-600" />
                                </div>
                                <span className="text-purple-600 font-semibold">{opp.assigned_sp}</span>
                            </>
                        ) : (
                            <span className="text-gray-300 italic">Unassigned</span>
                        )}
                    </div>
                </td>
            )}

            {role === 'GH' && (
                <td className="px-2 py-3">
                    <div className="flex flex-col gap-1 text-[10px]">
                        <div className="flex items-center gap-1">
                            <span className="text-gray-500 w-4">PH:</span>
                            <span className="font-medium">{opp.assigned_practice_head || '-'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <span className="text-gray-500 w-4">SH:</span>
                            <span className="font-medium">{opp.assigned_sales_head || '-'}</span>
                        </div>
                    </div>
                </td>
            )}

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
                {/* Review Actions - Only show if in Review state and approval pending for this role */}
                {opp.workflow_status === 'UNDER_REVIEW' && (
                    <div className="flex justify-end gap-2" onClick={e => e.stopPropagation()}>
                        {/* GH Action */}
                        {role === 'GH' && opp.gh_approval_status === 'PENDING' && (
                            <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                        )}
                        {/* PH Action */}
                        {role === 'PH' && opp.ph_approval_status === 'PENDING' && (
                            <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                        )}
                        {/* SH Action */}
                        {role === 'SH' && opp.sh_approval_status === 'PENDING' && (
                            <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                        )}
                    </div>
                )}

                {/* Assignment & View Actions */}
                <div className="flex flex-col gap-1 items-end mt-1" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-2">
                        {/* Show Assign button only if assignment is missing for this role */}
                        {role === 'PH' && !opp.assigned_sa && (
                            <AssignButton onClick={() => onAssign(opp, 'SA')} label="Assign SA" />
                        )}
                        {role === 'SH' && !opp.assigned_sp && (
                            <AssignButton onClick={() => onAssign(opp, 'SP')} label="Assign SP" />
                        )}
                        {role === 'GH' && (
                            <>
                                {!opp.assigned_practice_head && <AssignButton onClick={() => onAssign(opp, 'PH')} label="Assign PH" />}
                                {!opp.assigned_sales_head && <AssignButton onClick={() => onAssign(opp, 'SH')} label="Assign SH" />}
                            </>
                        )}

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

const ActionButtons = ({ onApprove, onReject }: { onApprove: () => void, onReject: () => void }) => (
    <>
        <button onClick={onApprove} className="px-2 py-1 text-[11px] font-bold bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] rounded hover:bg-[#C8E6C9] transition-colors flex items-center gap-1">
            <CheckCircle size={12} /> Accept
        </button>
        <button onClick={onReject} className="px-2 py-1 text-[11px] font-bold bg-[#FFEBEE] text-[#C62828] border border-[#FFCDD2] rounded hover:bg-[#FFCDD2] transition-colors flex items-center gap-1">
            <XCircle size={12} /> Reject
        </button>
    </>
);

const AssignButton = ({ onClick, label }: { onClick: () => void, label: string }) => (
    <button onClick={onClick} className="text-[10px] font-bold text-[#0572CE] hover:text-[#005a9e] uppercase border border-[#0572CE] px-1.5 py-0.5 rounded transition-colors flex items-center gap-1">
        <UserPlus size={10} /> {label}
    </button>
);
