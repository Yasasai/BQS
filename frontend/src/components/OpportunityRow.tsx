import React from 'react';
import { Opportunity } from '../types';
import { CheckCircle, XCircle, Link as LinkIcon, UserPlus } from 'lucide-react';

interface OpportunityRowProps {
    opp: Opportunity;
    onAssign: (opp: Opportunity, type?: 'PH' | 'SH' | 'SA' | 'SP') => void;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
    onView: (id: string, jumpToScore?: boolean) => void;
    onStartAssessment?: (id: string) => void;
    onContinueAssessment?: (id: string) => void;
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
    onStartAssessment,
    onContinueAssessment,
    formatCurrency,
    selected,
    onSelect,
    role = 'GH'
}) => {
    return (
        <tr
            className="hover:bg-gray-50 transition-colors border-b border-gray-100 text-[11px] h-10"
            onClick={() => onView(opp.id)}
        >
            <td className="px-4 py-1 border-r border-gray-100" onClick={e => e.stopPropagation()}>
                <input
                    type="checkbox"
                    className="w-3 h-3 rounded-sm border-gray-300 text-gray-700 focus:ring-gray-500"
                    checked={selected}
                    onChange={(e) => onSelect(opp.id, e.target.checked)}
                />
            </td>
            <td className="px-2 py-1 border-r border-gray-100">
                <span className="oracle-badge-green">
                    {opp.win_probability || 0}
                </span>
            </td>
            <td className="px-2 py-1 text-gray-600 border-r border-gray-100">
                {opp.remote_id}
            </td>
            <td className="px-2 py-1 oracle-link font-medium border-r border-gray-100">
                {opp.name}
            </td>
            <td className="px-2 py-1 text-gray-600 border-r border-gray-100">
                {opp.sales_owner || '-'}
            </td>
            <td className="px-2 py-1 text-gray-600 border-r border-gray-100">
                {opp.practice || '-'}
            </td>
            <td className="px-2 py-1 border-r border-gray-100">
                <span className="text-[10px] text-gray-700">4. Commit</span>
            </td>

            {/* Dynamic Assignment Column */}
            {role === 'PH' && (
                <td className="px-2 py-1 border-r border-gray-100">
                    <span className="text-gray-600 font-medium italic">{opp.assigned_sa || 'Unassigned'}</span>
                </td>
            )}

            {role === 'SH' && (
                <td className="px-2 py-1 border-r border-gray-100">
                    <span className="text-gray-600 font-medium italic">{opp.assigned_sp || 'Unassigned'}</span>
                </td>
            )}

            {role === 'GH' && (
                <td className="px-2 py-1 border-r border-gray-100">
                    <div className="flex flex-col gap-0.5 text-[9px] text-gray-500">
                        <div>PH: {opp.assigned_practice_head || '-'}</div>
                        <div>SH: {opp.assigned_sales_head || '-'}</div>
                    </div>
                </td>
            )}

            <td className="px-2 py-1 text-gray-600 border-r border-gray-100">
                {opp.stage_entered_at ? new Date(opp.stage_entered_at).toLocaleDateString() : '-'}
            </td>
            <td className="px-2 py-1 oracle-link border-r border-gray-100">
                {opp.customer}
            </td>
            <td className="px-2 py-1 text-gray-400 border-r border-gray-100">
                -
            </td>
            <td className="px-2 py-1 text-right text-gray-800 font-medium border-r border-gray-100">
                {formatCurrency(opp.deal_value)}
            </td>
            <td className="px-2 py-1 text-gray-600 border-r border-gray-100">
                {opp.estimated_billing_date || '-'}
            </td>
            <td className="px-2 py-1 border-r border-gray-100">
                <span className={`px-2 py-0.5 rounded border text-[10px] font-medium ${opp.stage?.includes('Commit') ? 'bg-green-50 border-green-200 text-green-700' :
                        opp.stage?.includes('Best Case') ? 'bg-blue-50 border-blue-200 text-blue-700' :
                            'bg-gray-50 border-gray-200 text-gray-600'
                    }`}>
                    {opp.stage || 'Lead'}
                </span>
            </td>
            <td className="px-2 py-1 text-gray-600 border-r border-gray-100 whitespace-nowrap overflow-hidden text-ellipsis max-w-[100px]">
                {opp.geo || opp.region || '-'}
            </td>
            <td className="px-2 py-1 text-right whitespace-nowrap">
                <div className="flex justify-end gap-1" onClick={e => e.stopPropagation()}>
                    {/* Review Actions */}
                    {['UNDER_REVIEW', 'READY_FOR_REVIEW', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SA_SUBMITTED', 'SP_SUBMITTED', 'SUBMITTED'].includes(opp.workflow_status || '') && (
                        <>
                            {role === 'GH' && opp.gh_approval_status === 'PENDING' && (
                                <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                            )}
                            {role === 'PH' && opp.ph_approval_status === 'PENDING' && (
                                <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                            )}
                            {role === 'SH' && opp.sh_approval_status === 'PENDING' && (
                                <ActionButtons onApprove={() => onApprove(opp.id)} onReject={() => onReject(opp.id)} />
                            )}
                        </>
                    )}

                    {/* Show Assign button only if assignment is missing for this role */}
                    {role === 'PH' && !opp.assigned_sa && (
                        <AssignButton onClick={() => onAssign(opp, 'SA')} label="Assign SA" />
                    )}
                    {role === 'SH' && (
                        <>
                            {!opp.assigned_sp && <AssignButton onClick={() => onAssign(opp, 'SP')} label="Assign SP" />}
                            {!opp.assigned_practice_head && <AssignButton onClick={() => onAssign(opp, 'PH')} label="Assign PH" />}
                        </>
                    )}
                    {role === 'GH' && (
                        <div className="flex gap-1">
                            <AssignButton onClick={() => onAssign(opp, 'PH')} label="PH" />
                            <AssignButton onClick={() => onAssign(opp, 'SH')} label="SH" />
                        </div>
                    )}

                    {(role === 'SA' || role === 'SP') && (
                        <>
                            {(['ASSIGNED_TO_SA', 'ASSIGNED_TO_SP', 'NEW', 'OPEN', 'HEADS_ASSIGNED'].includes(opp.workflow_status || 'NEW') || !opp.workflow_status) && onStartAssessment && (
                                <button onClick={() => onStartAssessment(opp.id)} className="oracle-btn">Start</button>
                            )}
                            {opp.workflow_status === 'UNDER_ASSESSMENT' && onContinueAssessment && (
                                <button onClick={() => onContinueAssessment(opp.id)} className="oracle-btn">Continue</button>
                            )}
                        </>
                    )}

                    {opp.version_no !== null && (
                        <button onClick={() => onView(opp.id, true)} className="oracle-btn !bg-orange-50 !border-orange-200">Score</button>
                    )}
                    <button onClick={() => onView(opp.id, false)} className="oracle-btn">View</button>
                </div>
            </td>
        </tr>
    );
};

const ActionButtons = ({ onApprove, onReject }: { onApprove: () => void, onReject: () => void }) => (
    <>
        <button onClick={onApprove} className="oracle-btn !bg-green-50 !border-green-200 !text-green-700">Accept</button>
        <button onClick={onReject} className="oracle-btn !bg-red-50 !border-red-200 !text-red-700">Reject</button>
    </>
);

const AssignButton = ({ onClick, label }: { onClick: () => void, label: string }) => (
    <button onClick={onClick} className="oracle-btn !text-blue-600 !border-blue-100">{label}</button>
);
