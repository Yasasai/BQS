import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronDown, MoreHorizontal, Filter, UserPlus, CheckCircle, XCircle, RefreshCw, Download, Link as LinkIcon, Search, TrendingUp, Users } from 'lucide-react';
import { AssignArchitectModal, AssignmentData } from '../components/AssignArchitectModal';
import { OpportunitiesTable } from '../components/OpportunitiesTable';
import { Pagination } from '../components/Pagination';
import { ManageUsersModal } from '../components/ManageUsersModal';

type TabType = 'all' | 'unassigned' | 'assigned' | 'review' | 'completed';

const TAB_LABELS: Record<string, string> = {
    'all': 'All Opportunities',
    'unassigned': 'Assign Pipeline',
    'assigned': 'Work Pipeline',
    'review': 'Review Pipeline',
    'completed': 'Completed Assessments'
};

export function PracticeHeadDashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const location = useLocation();

    // Data State
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [globalPipelineValue, setGlobalPipelineValue] = useState(0);
    const [tabCounts, setTabCounts] = useState<Record<string, number>>({});

    // Pagination & Search State
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(50);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');

    const [activeTab, setActiveTab] = useState<TabType>('unassigned');
    const [viewMode, setViewMode] = useState('All Opportunities');

    // Modal state
    const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
    const [isUserModalOpen, setIsUserModalOpen] = useState(false);
    const [selectedOppId, setSelectedOppId] = useState<string[]>([]);

    // Action menu state
    const [openActionMenu, setOpenActionMenu] = useState<string | null>(null);

    // Role-based Access Control
    useEffect(() => {
        if (user?.role === 'SOLUTION_ARCHITECT') {
            navigate('/assigned-to-me');
        }
    }, [user, navigate]);

    // Sync URL with Tab
    useEffect(() => {
        const path = location.pathname;
        if (path.includes('unassigned')) setActiveTab('unassigned');
        else if (path.includes('assigned')) setActiveTab('assigned');
        else if (path.includes('review')) setActiveTab('review');
        else if (path.includes('completed')) setActiveTab('completed');
        else setActiveTab('all');
    }, [location.pathname]);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchTerm);
            setCurrentPage(1); // Reset to page 1 on search
        }, 500);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    // Fetch on changes
    useEffect(() => {
        fetchOpportunities();
        setSelectedOppId([]); // Clear selection when tab/page/search changes
    }, [currentPage, pageSize, debouncedSearch, activeTab]);

    const fetchOpportunities = () => {
        console.log('🔄 Fetching opportunities page:', currentPage, 'Tab:', activeTab);
        setLoading(true);

        const params = new URLSearchParams({
            page: currentPage.toString(),
            limit: pageSize.toString(),
            tab: activeTab
        });
        if (debouncedSearch) params.append('search', debouncedSearch);

        fetch(`http://127.0.0.1:8000/api/opportunities/?${params}`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log('✅ Received data:', data);
                if (data.items) {
                    setOpportunities(data.items);
                    setTotalCount(data.total_count);
                    setGlobalPipelineValue(data.total_value || 0);
                    if (data.counts) setTabCounts(data.counts);
                } else {
                    setOpportunities(data);
                    setTotalCount(data.length);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error("❌ Failed to fetch opportunities:", err);
                setLoading(false);
            });
    };


    // --- filtering for Display ---
    const filteredOpportunities = opportunities;

    const handleAssignToSA = async (oppIds: string | string[], primarySA: string, secondarySA?: string) => {
        const idsToAssign = Array.isArray(oppIds) ? oppIds : [oppIds];
        try {
            await Promise.all(idsToAssign.map(id =>
                fetch('http://127.0.0.1:8000/api/inbox/assign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        opp_id: id.toString(),
                        sa_email: primarySA,
                        assigned_by_user_id: user?.id || 'PRACTICE_HEAD'
                    })
                })
            ));
            fetchOpportunities();
            setIsAssignModalOpen(false);
            setSelectedOppId([]);
        } catch (err) {
            console.error('❌ Assignment error:', err);
            alert(`Failed to assign: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
    };

    const handleApprove = async (oppIds: string | string[]) => {
        const ids = Array.isArray(oppIds) ? oppIds : [oppIds];
        if (!confirm(`Approve ${ids.length} assessment(s)?`)) return;
        try {
            await Promise.all(ids.map(id =>
                fetch(`http://127.0.0.1:8000/api/scoring/${id}/review/approve`, { method: 'POST' })
            ));
            fetchOpportunities();
            setSelectedOppId([]);
        } catch (e) {
            console.error(e);
            alert("Approval failed");
        }
    };

    const handleReject = async (oppIds: string | string[]) => {
        const ids = Array.isArray(oppIds) ? oppIds : [oppIds];
        const reason = prompt("Enter rejection reason for selected items:");
        if (!reason) return;
        try {
            await Promise.all(ids.map(id =>
                fetch(`http://127.0.0.1:8000/api/scoring/${id}/review/reject`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason })
                })
            ));
            fetchOpportunities();
            setSelectedOppId([]);
        } catch (e) {
            console.error(e);
            alert("Rejection failed");
        }
    };

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-gray-900 overflow-x-hidden">
            <TopBar title="Practice Head Dashboard" />
            <div className="flex-1 px-4 py-4 w-full max-w-[1600px] mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-normal text-[#333333]">Opportunities</h1>
                        <div className="w-5 h-5 rounded-full border border-gray-400 flex items-center justify-center text-[10px] text-gray-500 cursor-help">?</div>
                    </div>
                    <button
                        onClick={() => setIsUserModalOpen(true)}
                        className="flex items-center gap-2 px-3 py-1.5 text-[13px] font-normal text-[#333333] border border-gray-300 rounded bg-white hover:bg-gray-50"
                    >
                        <Users size={14} /> Manage Users
                    </button>
                </div>


                {/* Tab Switcher */}
                <div className="flex items-center gap-8 border-b border-gray-200 mb-6 mt-4">
                    {(Object.keys(TAB_LABELS) as TabType[]).map((tabId) => (
                        <button
                            key={tabId}
                            onClick={() => navigate(`/practice-head/${tabId}`)}
                            className={`pb-3 text-sm font-medium transition-all relative ${activeTab === tabId
                                ? 'text-[#0572CE]'
                                : 'text-[#666666] hover:text-[#333333]'
                                }`}
                        >
                            {TAB_LABELS[tabId]} ({tabCounts[tabId] || 0})
                            {activeTab === tabId && (
                                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0572CE]" />
                            )}
                        </button>
                    ))}
                </div>

                <div className="flex items-center justify-between py-2 mb-4 text-xs">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <span className="text-[13px] text-[#333333]">Find</span>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search Name, Customer..."
                                    className="border border-gray-300 rounded px-2 py-1.5 text-[13px] w-64 focus:outline-none focus:border-[#0572CE] bg-white pl-8"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                                <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button onClick={() => fetchOpportunities()} className="flex items-center gap-2 px-4 py-1.5 text-[13px] font-normal text-[#333333] bg-white border border-gray-300 rounded hover:bg-gray-50">
                            <RefreshCw size={14} /> Refresh
                        </button>
                        <button className="px-4 py-1.5 text-[13px] font-normal text-white bg-[#0572CE] rounded hover:bg-[#005a9e]">Create Opportunity</button>
                    </div>
                </div>

                {selectedOppId.length > 0 && (
                    <div className="bg-[#E3F2FD] border border-[#BBDEFB] px-4 py-2 mb-4 rounded flex items-center justify-between">
                        <span className="text-sm font-medium text-[#0D47A1]">{selectedOppId.length} item(s) selected</span>
                        <div className="flex gap-2">
                            {(() => {
                                const selectedItems = opportunities.filter(o => selectedOppId.includes(o.id));
                                const canAssign = selectedItems.length > 0; // Allow assigning/reassigning everything as requested
                                const canReview = selectedItems.length > 0 && selectedItems.every(o => {
                                    const s = (o.workflow_status || '').toUpperCase();
                                    return s === 'SUBMITTED_FOR_REVIEW' || s === 'SUBMITTED';
                                });
                                return (
                                    <>
                                        {canAssign && (
                                            <button onClick={() => setIsAssignModalOpen(true)} className="px-3 py-1 bg-[#1976D2] text-white text-xs font-medium rounded hover:bg-[#1565C0]">Assign / Reassign Selected</button>
                                        )}
                                        {canReview && (
                                            <>
                                                <button onClick={() => handleApprove(selectedOppId)} className="px-3 py-1 bg-[#43A047] text-white text-xs font-medium rounded hover:bg-[#2E7D32]">Accept Selected</button>
                                                <button onClick={() => handleReject(selectedOppId)} className="px-3 py-1 bg-[#E53935] text-white text-xs font-medium rounded hover:bg-[#C62828]">Reject Selected</button>
                                            </>
                                        )}
                                    </>
                                );
                            })()}
                        </div>
                    </div>
                )}

                <div className="flex items-center gap-2 mb-2">
                    <span className="text-[13px] text-[#333333] font-medium">{TAB_LABELS[activeTab] || 'Opportunities'}</span>
                </div>

                <OpportunitiesTable
                    opportunities={filteredOpportunities}
                    loading={loading}
                    onAssign={(opp) => { setSelectedOppId([opp.id]); setIsAssignModalOpen(true); }}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    onView={(id, jumpToScore) => {
                        if (jumpToScore) {
                            navigate(`/score/${id}`);
                        } else {
                            navigate(`/opportunity/${id}`);
                        }
                    }}
                    formatCurrency={formatCurrency}
                    selectedIds={selectedOppId}
                    onSelectionChange={setSelectedOppId}
                />

                <div className="mt-[-48px] relative z-10">
                    <Pagination
                        currentPage={currentPage}
                        totalCount={totalCount}
                        pageSize={pageSize}
                        onPageChange={setCurrentPage}
                    />
                </div>
            </div>

            <AssignArchitectModal
                isOpen={isAssignModalOpen}
                onClose={() => setIsAssignModalOpen(false)}
                opportunityIds={selectedOppId}
                onAssign={(data: AssignmentData) => { handleAssignToSA(selectedOppId, data.sa_owner, data.secondary_sa); }}
            />
            <ManageUsersModal isOpen={isUserModalOpen} onClose={() => setIsUserModalOpen(false)} />
        </div>
    );
}
