import React from 'react';
import { Opportunity } from '../types';
import { OpportunityRow } from './OpportunityRow';
import { RefreshCw } from 'lucide-react';

interface OpportunitiesTableProps {
    opportunities: Opportunity[];
    loading: boolean;
    onAssign: (opp: Opportunity) => void;
    onApprove: (id: number) => void;
    onReject: (id: number) => void;
    onView: (id: number) => void;
    formatCurrency: (val: number) => string;
}

export const OpportunitiesTable: React.FC<OpportunitiesTableProps> = ({
    opportunities,
    loading,
    onAssign,
    onApprove,
    onReject,
    onView,
    formatCurrency
}) => {
    return (
        <div className="bg-white border-x border-b border-gray-200 rounded-b-lg overflow-x-auto shadow-sm mb-12">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-[#F9FAFB] border-b border-gray-200">
                    <tr>
                        <th className="px-4 py-4 text-left w-10">
                            {/* Header Checkbox */}
                        </th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Win (%)</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Opportunity Nbr</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Name</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Owner</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Practice</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Status</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Creation Date</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Account</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Account Owner</th>
                        <th className="px-2 py-4 text-right text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Amount</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Est. Billing</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Sales Stage</th>
                        <th className="px-2 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Region</th>
                        <th className="px-2 py-4 text-right text-xs font-semibold text-[#4B5563] uppercase tracking-wider tracking-widest px-6">Actions</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                    {loading ? (
                        <tr><td colSpan={15} className="px-6 py-32 text-center">
                            <div className="flex flex-col items-center gap-4">
                                <RefreshCw size={40} className="text-[#2563EB] animate-spin" />
                                <span className="text-sm font-semibold text-[#6B7280] uppercase tracking-widest">Hydrating Pipeline Data...</span>
                            </div>
                        </td></tr>
                    ) : opportunities.length === 0 ? (
                        <tr><td colSpan={15} className="px-6 py-24 text-center text-gray-400 font-medium">No results matched your current filters.</td></tr>
                    ) : (
                        opportunities.map((opp) => (
                            <OpportunityRow
                                key={opp.id}
                                opp={opp}
                                onAssign={onAssign}
                                onApprove={onApprove}
                                onReject={onReject}
                                onView={onView}
                                formatCurrency={formatCurrency}
                            />
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
};
