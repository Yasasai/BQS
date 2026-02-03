import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { RefreshCw, PlayCircle, CheckCircle, Clock } from 'lucide-react';
import { Opportunity } from '../types';

interface MyAssignment {
    opp_id: string;
    row_id?: string;
    opp_number: string;
    opp_name: string;
    customer_name: string;
    deal_value: number;
    crm_last_updated_at: string;
    latest_score_status: string; // 'NOT_STARTED', 'DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED'
    version_no?: number;
}

export function SolutionArchitectDashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [assignments, setAssignments] = useState<MyAssignment[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');

    // Metrics Helpers
    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
    const formatLargeNumber = (num: number) => {
        if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `$${(num / 1000).toFixed(0)}K`;
        return `$${num}`;
    };

    // Metrics Calculations
    const activeCount = assignments.filter(a => ['NOT_STARTED', 'DRAFT', 'UNDER_ASSESSMENT', 'ASSIGNED_TO_SA'].includes(a.latest_score_status.toUpperCase())).length;
    const totalValue = assignments.reduce((acc, curr) => acc + (curr.deal_value || 0), 0);
    const completedCount = assignments.filter(a => ['APPROVED', 'REJECTED', 'SUBMITTED', 'COMPLETED', 'WON', 'LOST', 'ACCEPTED'].includes(a.latest_score_status.toUpperCase())).length;

    // Filtering logic
    const filteredAssignments = assignments.filter(a => {
        const status = a.latest_score_status.toUpperCase();
        if (activeTab === 'active') {
            return ['NOT_STARTED', 'DRAFT', 'UNDER_ASSESSMENT', 'ASSIGNED_TO_SA'].includes(status);
        } else {
            return ['APPROVED', 'REJECTED', 'SUBMITTED', 'COMPLETED', 'WON', 'LOST', 'ACCEPTED'].includes(status);
        }
    });

    const fetchAssignments = React.useCallback(() => {
        if (!user?.id) return;
        // Only show full loading state if we have no data, otherwise background refresh
        if (assignments.length === 0) setLoading(true);

        // Ensure we pass the actual user ID.
        fetch(`http://127.0.0.1:8000/api/inbox/my-assignments?user_id=${user.id}`)
            .then(res => res.json())
            .then(data => {
                setAssignments(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch assignments", err);
                setLoading(false);
            });
    }, [user?.id, assignments.length]);

    // Initial Load
    useEffect(() => {
        fetchAssignments();
    }, [fetchAssignments]);

    // Auto-Refresh on Focus & Interval
    useEffect(() => {
        const onFocus = () => {
            console.log("⚡ Tab Focused: Refreshing Data...");
            fetchAssignments();
        };

        window.addEventListener("focus", onFocus);
        const interval = setInterval(fetchAssignments, 15000); // Poll every 15s

        return () => {
            window.removeEventListener("focus", onFocus);
            clearInterval(interval);
        };
    }, [fetchAssignments]);

    const handleStartAssessment = (oppId: string) => {
        // Navigate to scoring page
        navigate(`/score/${oppId}`);
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900 overflow-x-hidden">
            <TopBar title="Solution Architect Dashboard" />

            <div className="flex-1 px-4 py-4 w-full max-w-[1600px] mx-auto">

                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-normal text-[#333333]">My Assignments</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-500 cursor-help">?</div>
                    </div>
                </div>

                {/* Metrics Grid - Enterprise Style */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {/* Active Assignments Card */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">ACTIVE ASSIGNMENTS</div>
                        <div>
                            <div className="text-4xl font-normal text-[#0572CE]">{activeCount}</div>
                            <div className="text-[11px] text-[#666666] mt-1">Pending Completion</div>
                        </div>
                    </div>

                    {/* Pipeline Value Card */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">MY PIPELINE VALUE</div>
                        <div>
                            <div className="text-4xl font-normal text-[#217346]">{formatLargeNumber(totalValue)}</div>
                            <div className="text-[11px] text-[#666666] mt-1">{formatCurrency(totalValue)}</div>
                        </div>
                    </div>

                    {/* Completed Card */}
                    <div className="bg-white p-5 rounded border border-gray-200 shadow-sm flex flex-col justify-between h-36">
                        <div className="text-[11px] font-semibold text-[#666666] uppercase tracking-wide">COMPLETED ASSESSMENTS</div>
                        <div>
                            <div className="text-4xl font-normal text-[#607D8B]">{completedCount}</div>
                            <div className="text-[11px] text-[#666666] mt-1">Past Reviews</div>
                        </div>
                    </div>
                </div>

                {/* Tab Switcher */}
                <div className="flex items-center gap-8 border-b border-gray-200 mb-6">
                    <button
                        onClick={() => setActiveTab('active')}
                        className={`pb-3 text-sm font-medium transition-all relative ${activeTab === 'active'
                            ? 'text-[#0572CE]'
                            : 'text-[#666666] hover:text-[#333333]'
                            }`}
                    >
                        Active Tasks ({activeCount})
                        {activeTab === 'active' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0572CE]" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`pb-3 text-sm font-medium transition-all relative ${activeTab === 'history'
                            ? 'text-[#0572CE]'
                            : 'text-[#666666] hover:text-[#333333]'
                            }`}
                    >
                        History ({completedCount})
                        {activeTab === 'history' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0572CE]" />
                        )}
                    </button>
                </div>

                {/* Toolbar */}
                <div className="flex items-center justify-end mb-4">
                    <button
                        onClick={fetchAssignments}
                        className="flex items-center gap-2 px-4 py-1.5 text-[13px] font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50"
                    >
                        <RefreshCw size={14} /> Refresh
                    </button>
                </div>

                {/* Table */}
                <div className="bg-white border-x border-b border-gray-200 rounded shadow-sm overflow-hidden mb-12">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-[#F9FAFB] border-b border-gray-200">
                            <tr>
                                <th className="px-4 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Opportunity Name</th>
                                <th className="px-4 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Customer</th>
                                <th className="px-4 py-4 text-right text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Value</th>
                                <th className="px-4 py-4 text-left text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Assessment Status</th>
                                <th className="px-4 py-4 text-right text-xs font-semibold text-[#4B5563] uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-100">
                            {loading ? (
                                <tr><td colSpan={5} className="px-6 py-24 text-center">
                                    <div className="flex flex-col items-center gap-4">
                                        <RefreshCw size={32} className="text-[#0572CE] animate-spin" />
                                        <span className="text-sm font-semibold text-[#6B7280] uppercase tracking-widest">Loading Assignments...</span>
                                    </div>
                                </td></tr>
                            ) : filteredAssignments.length === 0 ? (
                                <tr><td colSpan={5} className="px-6 py-24 text-center text-gray-400 font-medium">
                                    <div className="flex flex-col items-center gap-2">
                                        <CheckCircle className="text-emerald-300" size={48} />
                                        <span>No {activeTab} assignments found.</span>
                                    </div>
                                </td></tr>
                            ) : (
                                filteredAssignments.map((assign) => (
                                    <tr key={assign.row_id || assign.opp_id} className="hover:bg-gray-50 transition-colors group">
                                        <td className="px-4 py-4">
                                            <div className="text-[14px] font-medium text-[#0572ce] hover:underline cursor-pointer">{assign.opp_name}</div>
                                            <div className="text-[11px] text-[#6B7280]">{assign.opp_number || assign.opp_id}</div>
                                        </td>
                                        <td className="px-4 py-4 text-[13px] text-[#374151]">{assign.customer_name}</td>
                                        <td className="px-4 py-4 text-right text-[13px] font-semibold text-[#111827]">
                                            {formatCurrency(assign.deal_value)}
                                        </td>
                                        <td className="px-4 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium ${assign.latest_score_status.toUpperCase() === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                                                assign.latest_score_status.toUpperCase() === 'SUBMITTED' ? 'bg-amber-100 text-amber-800' :
                                                    assign.latest_score_status.toUpperCase() === 'REJECTED' ? 'bg-rose-100 text-rose-800' :
                                                        'bg-blue-50 text-blue-800'
                                                }`}>
                                                {assign.latest_score_status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 text-right">
                                            <button
                                                onClick={() => handleStartAssessment(assign.opp_id)}
                                                className={`px-4 py-1.5 text-xs font-semibold rounded-md transition-all shadow-sm ${['SUBMITTED', 'APPROVED', 'REJECTED', 'COMPLETED', 'WON', 'LOST', 'ACCEPTED'].includes(assign.latest_score_status.toUpperCase())
                                                    ? 'bg-white border border-gray-300 text-[#374151] hover:bg-gray-50'
                                                    : 'bg-[#0572CE] text-white hover:bg-[#005a9e]'
                                                    }`}
                                            >
                                                {['SUBMITTED', 'APPROVED', 'REJECTED', 'COMPLETED', 'WON', 'LOST', 'ACCEPTED'].includes(assign.latest_score_status.toUpperCase()) ? 'View' :
                                                    ['NOT_STARTED', 'ASSIGNED_TO_SA'].includes(assign.latest_score_status.toUpperCase()) ? 'Start' : 'Continue'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
