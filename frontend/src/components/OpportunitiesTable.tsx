import React, { useState, useEffect, useRef } from 'react';
import { Opportunity } from '../types';
import { OpportunityRow } from './OpportunityRow';
import { RefreshCw, Filter, X, ChevronDown, ChevronUp } from 'lucide-react';

export interface FilterState {
    id: string;
    value: any; // Can be string, string[], or {min, max}
}

interface OpportunitiesTableProps {
    opportunities: Opportunity[];
    loading: boolean;
    onAssign: (opp: Opportunity, type?: 'PH' | 'SH' | 'SA' | 'SP') => void;
    onApprove: (id: string) => void;
    onReject: (id: string) => void;
    onView: (id: string, jumpToScore?: boolean) => void;
    onStartAssessment?: (id: string) => void;
    onContinueAssessment?: (id: string) => void;
    formatCurrency: (val: number) => string;
    selectedIds: string[];
    onSelectionChange: (ids: string[]) => void;
    role?: 'GH' | 'PH' | 'SH' | 'SA' | 'SP';
    filters?: FilterState[];
    onFilterChange?: (filters: FilterState[]) => void;
    metadata?: {
        regions?: string[];
        practices?: string[];
        stages?: string[];
        statuses?: string[];
    };
}

export const OpportunitiesTable: React.FC<OpportunitiesTableProps> = ({
    opportunities,
    loading,
    onAssign,
    onApprove,
    onReject,
    onView,
    onStartAssessment,
    onContinueAssessment,
    formatCurrency,
    selectedIds,
    onSelectionChange,
    role = 'GH',
    filters = [],
    onFilterChange = () => { },
    metadata
}) => {
    // Select All Logic
    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            onSelectionChange(opportunities.map(o => o.id));
        } else {
            onSelectionChange([]);
        }
    };

    const handleSelectRow = (id: string, checked: boolean) => {
        if (checked) {
            onSelectionChange([...selectedIds, id]);
        } else {
            onSelectionChange(selectedIds.filter(sid => sid !== id));
        }
    };

    const allSelected = opportunities.length > 0 && opportunities.every(o => selectedIds.includes(o.id));
    const someSelected = opportunities.some(o => selectedIds.includes(o.id));

    // Filter Logic
    const [activeFilterCol, setActiveFilterCol] = useState<string | null>(null);
    const filterRef = useRef<HTMLDivElement>(null);

    // Range Filter State
    const [rangeMin, setRangeMin] = useState<string>('');
    const [rangeMax, setRangeMax] = useState<string>('');

    // Multi-select search
    const [filterSearch, setFilterSearch] = useState('');

    // Close filter on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
                setActiveFilterCol(null);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const openFilter = (col: string) => {
        const existing = filters.find(f => f.id === col);
        if (col === 'deal_value') {
            const val = existing?.value || {};
            setRangeMin(val.min?.toString() || '');
            setRangeMax(val.max?.toString() || '');
        }
        setFilterSearch('');
        setActiveFilterCol(activeFilterCol === col ? null : col);
    };

    const applyMultiFilter = (col: string, values: string[]) => {
        const newFilters = filters.filter(f => f.id !== col);
        if (values.length > 0) {
            newFilters.push({ id: col, value: values });
        }
        onFilterChange(newFilters);
    };

    const applyRangeFilter = (col: string) => {
        const newFilters = filters.filter(f => f.id !== col);
        const min = rangeMin ? parseFloat(rangeMin) : undefined;
        const max = rangeMax ? parseFloat(rangeMax) : undefined;

        if (min !== undefined || max !== undefined) {
            newFilters.push({ id: col, value: { min, max } });
        }
        onFilterChange(newFilters);
        setActiveFilterCol(null);
    };

    const getUniqueValues = (colId: string) => {
        if (colId === 'geo' && metadata?.regions && metadata.regions.length > 0) return [...metadata.regions].sort();
        if (colId === 'practice' && metadata?.practices && metadata.practices.length > 0) return [...metadata.practices].sort();
        if ((colId === 'sales_stage' || colId === 'Sales Stage') && metadata?.stages && metadata.stages.length > 0) return [...metadata.stages].sort();
        if ((colId === 'workflow_status' || colId === 'Status') && metadata?.statuses && metadata.statuses.length > 0) return [...metadata.statuses].sort();

        const vals = opportunities.map(o => {
            const val = (o as any)[colId];
            return val === null || val === undefined ? '(Blank)' : String(val);
        });
        return Array.from(new Set(vals)).sort();
    };

    const renderHeader = (label: string, colId: string, align: 'left' | 'right' = 'left', isRange = false) => {
        const isFiltered = filters.some(f => f.id === colId);
        const uniqueValues = !isRange ? getUniqueValues(colId) : [];
        const currentFilter = filters.find(f => f.id === colId);
        const selectedValues = Array.isArray(currentFilter?.value) ? currentFilter?.value : [];

        return (
            <th className={`px-2 py-2 text-${align} text-[11px] font-bold text-gray-800 border-r border-gray-100 group relative`}>
                <div className={`flex items-center gap-1 cursor-pointer hover:text-blue-600 ${align === 'right' ? 'justify-end' : ''}`} onClick={(e) => { e.stopPropagation(); openFilter(colId); }}>
                    {label}
                    <Filter size={10} className={isFiltered ? "text-blue-600 fill-blue-600" : "text-gray-300 group-hover:text-blue-400"} />
                </div>

                {activeFilterCol === colId && (
                    <div ref={filterRef} className="absolute top-full left-0 mt-1 bg-white border border-gray-200 shadow-xl rounded-sm p-0 z-50 w-56 text-left font-normal normal-case" onClick={e => e.stopPropagation()}>
                        <div className="p-2 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                            <span className="text-[10px] font-bold text-gray-500 uppercase">Filter {label}</span>
                            <button onClick={() => setActiveFilterCol(null)}><X size={12} className="text-gray-400 hover:text-red-500" /></button>
                        </div>

                        {isRange ? (
                            <div className="p-3 space-y-3">
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="text-[9px] text-gray-400 font-bold uppercase">Min</label>
                                        <input
                                            type="number"
                                            className="w-full px-2 py-1 text-xs border border-gray-200 rounded outline-none focus:border-blue-500"
                                            value={rangeMin}
                                            onChange={e => setRangeMin(e.target.value)}
                                            placeholder="0"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-[9px] text-gray-400 font-bold uppercase">Max</label>
                                        <input
                                            type="number"
                                            className="w-full px-2 py-1 text-xs border border-gray-200 rounded outline-none focus:border-blue-500"
                                            value={rangeMax}
                                            onChange={e => setRangeMax(e.target.value)}
                                            placeholder="Max"
                                        />
                                    </div>
                                </div>
                                <div className="flex justify-between gap-2 pt-2">
                                    <button
                                        onClick={() => { setRangeMin(''); setRangeMax(''); onFilterChange(filters.filter(f => f.id !== colId)); setActiveFilterCol(null); }}
                                        className="text-[10px] font-bold text-gray-400 hover:text-gray-600"
                                    >Clear</button>
                                    <button
                                        onClick={() => applyRangeFilter(colId)}
                                        className="px-3 py-1 bg-[#5c5c5c] text-white text-[10px] font-bold rounded hover:bg-black"
                                    >Apply</button>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col max-h-64">
                                <div className="p-2">
                                    <input
                                        type="text"
                                        placeholder="Search values..."
                                        className="w-full px-2 py-1 text-xs border border-gray-200 rounded outline-none"
                                        value={filterSearch}
                                        onChange={e => setFilterSearch(e.target.value)}
                                    />
                                </div>
                                <div className="overflow-y-auto px-2 pb-2 space-y-1">
                                    <label className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer text-xs">
                                        <input
                                            type="checkbox"
                                            checked={selectedValues.length === uniqueValues.length}
                                            onChange={(e) => {
                                                if (e.target.checked) applyMultiFilter(colId, uniqueValues);
                                                else applyMultiFilter(colId, []);
                                            }}
                                            className="w-3 h-3 rounded-sm text-blue-600"
                                        />
                                        <span className="font-bold">(Select All)</span>
                                    </label>
                                    {uniqueValues.filter(v => v.toLowerCase().includes(filterSearch.toLowerCase())).map(val => (
                                        <label key={val} className="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer text-xs">
                                            <input
                                                type="checkbox"
                                                checked={selectedValues.includes(val)}
                                                onChange={(e) => {
                                                    const next = e.target.checked
                                                        ? [...selectedValues, val]
                                                        : selectedValues.filter(v => v !== val);
                                                    applyMultiFilter(colId, next);
                                                }}
                                                className="w-3 h-3 rounded-sm text-blue-600"
                                            />
                                            <span className="truncate">{val}</span>
                                        </label>
                                    ))}
                                </div>
                                <div className="p-2 border-t border-gray-100 bg-gray-50 flex justify-end">
                                    <button onClick={() => setActiveFilterCol(null)} className="px-3 py-1 bg-[#5c5c5c] text-white text-[10px] font-bold rounded hover:bg-black">Close</button>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </th>
        );
    };

    return (
        <div className="bg-white border border-gray-200 rounded-sm overflow-x-auto mb-12" style={{ minHeight: '400px' }}>
            <table className="min-w-full border-collapse">
                <thead className="oracle-table-header">
                    <tr className="border-b-2 border-gray-200">
                        <th className="px-4 py-2 text-left w-10 border-r border-gray-100">
                            <input
                                type="checkbox"
                                className="w-3.5 h-3.5 rounded-sm border-gray-300 text-gray-700 focus:ring-gray-500 cursor-pointer"
                                checked={allSelected}
                                ref={input => { if (input) input.indeterminate = someSelected && !allSelected; }}
                                onChange={(e) => handleSelectAll(e.target.checked)}
                            />
                        </th>
                        {renderHeader('Win (%)', 'win_probability')}
                        {renderHeader('Opportunity Nbr', 'remote_id')}
                        {renderHeader('Name', 'name')}
                        {renderHeader('Owner', 'owner')}
                        {renderHeader('Practice', 'practice')}
                        {renderHeader('Status', 'workflow_status')}

                        {/* Dynamic Assignment Header */}
                        {role === 'PH' && renderHeader('Assigned Architect', 'assigned_sa')}
                        {role === 'SH' && renderHeader('Assigned Sales Rep', 'assigned_sp')}
                        {role === 'GH' && <th className="px-2 py-2 text-left text-[11px] font-bold text-gray-800 border-r border-gray-100 italic">Assignments</th>}

                        {renderHeader('Creation Date', 'created_at')}
                        {renderHeader('Account', 'customer')}
                        {renderHeader('Account Owner', 'account_owner')}
                        {renderHeader('Amount', 'deal_value', 'right', true)}
                        {renderHeader('Est. Billing', 'estimated_billing_date')}
                        {renderHeader('Sales Stage', 'sales_stage')}
                        {renderHeader('Region', 'geo')}
                        <th className="px-2 py-2 text-right text-[11px] font-bold text-gray-800 whitespace-nowrap">Actions</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                    {loading ? (
                        <tr><td colSpan={16} className="px-6 py-32 text-center">
                            <div className="flex flex-col items-center gap-4">
                                <RefreshCw size={32} className="text-gray-400 animate-spin" />
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-widest">Loading Data...</span>
                            </div>
                        </td></tr>
                    ) : opportunities.length === 0 ? (
                        <tr><td colSpan={16} className="px-6 py-24 text-center text-gray-400 text-sm italic">No data matching filters.</td></tr>
                    ) : (
                        opportunities.map((opp) => (
                            <OpportunityRow
                                key={opp.row_id || opp.id}
                                opp={opp}
                                onAssign={onAssign}
                                onApprove={onApprove}
                                onReject={onReject}
                                onView={onView}
                                onStartAssessment={onStartAssessment}
                                onContinueAssessment={onContinueAssessment}
                                formatCurrency={formatCurrency}
                                selected={selectedIds.includes(opp.id)}
                                onSelect={handleSelectRow}
                                role={role}
                            />
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
};
