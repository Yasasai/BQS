import React, { useState, useEffect } from 'react';
import { RefreshCw, Database, Terminal, Settings, AlertCircle, CheckCircle, UserPlus, Edit2, Trash2, Globe, Briefcase, X, Save, UserCheck, ChevronDown, RotateCcw, Lock } from 'lucide-react';
import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { useAuth } from '../context/AuthContext';
import { User } from '../types';

const AdminDashboard: React.FC = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState<'sync' | 'users' | 'opportunities' | 'opps-mgmt'>('users');

    // Sync States
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncMessage, setSyncMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
    const [syncStatus, setSyncStatus] = useState<any>(null);

    // User Management States
    const [users, setUsers] = useState<User[]>([]);
    const [isLoadingUsers, setIsLoadingUsers] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<User | null>(null);
    const [formData, setFormData] = useState<Partial<User>>({
        email: '',
        display_name: '',
        roles: ['SA'],
        manager_email: '',
        geo_region: '',
        practice_name: '',
        is_active: true
    });

    // Opportunity Assignment States
    const [opportunities, setOpportunities] = useState<any[]>([]);
    const [isLoadingOpps, setIsLoadingOpps] = useState(false);
    const [bmUsers, setBmUsers] = useState<any[]>([]);
    const [assignModal, setAssignModal] = useState<{ opp: any } | null>(null);
    const [selectedBmId, setSelectedBmId] = useState('');
    const [assigning, setAssigning] = useState(false);
    const [assignMessage, setAssignMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [oppStatusFilter, setOppStatusFilter] = useState<'OPEN' | 'ACTIVE' | 'all'>('OPEN');

    // Opportunity Management States (view all / reopen)
    const [oppMgmtFilter, setOppMgmtFilter] = useState<'all' | 'OPEN' | 'ACTIVE' | 'CLOSED' | 'REOPENED'>('all');
    const [reopening, setReopening] = useState<string | null>(null);
    const [reopenMsg, setReopenMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const fetchSyncStatus = async () => {
        try {
            const response = await apiClient.get(API_ENDPOINTS.BATCH_SYNC.STATUS);
            setSyncStatus(response.data);
        } catch (err) {
            console.error("Failed to fetch sync status:", err);
        }
    };

    const fetchUsers = async () => {
        setIsLoadingUsers(true);
        try {
            const response = await apiClient.get('/api/admin/users/');
            setUsers(response.data);
        } catch (err) {
            console.error("Failed to fetch users:", err);
        } finally {
            setIsLoadingUsers(false);
        }
    };

    const fetchOpportunities = async () => {
        setIsLoadingOpps(true);
        try {
            const response = await apiClient.get('/api/opportunities/?limit=200&page=1');
            const data = response.data;
            setOpportunities(data.items || data.opportunities || []);
        } catch (err) {
            console.error("Failed to fetch opportunities:", err);
        } finally {
            setIsLoadingOpps(false);
        }
    };

    const fetchBMUsers = async () => {
        try {
            const response = await apiClient.get('/api/users/?role=BM');
            setBmUsers(response.data || []);
        } catch (err) {
            console.error("Failed to fetch BM users:", err);
        }
    };

    const handleReopen = async (opp: any) => {
        if (!window.confirm(`Reopen "${opp.name}"? It will transition to REOPENED and the Bid Manager can be reassigned.`)) return;
        setReopening(opp.id);
        setReopenMsg(null);
        try {
            await apiClient.post(`/api/opportunities/${opp.id}/reopen`);
            setReopenMsg({ type: 'success', text: `"${opp.name}" has been reopened successfully.` });
            await fetchOpportunities();
        } catch (err: any) {
            setReopenMsg({ type: 'error', text: err?.response?.data?.detail || 'Failed to reopen opportunity.' });
        } finally {
            setReopening(null);
        }
    };

    const handleAssignBM = async () => {
        if (!assignModal || !selectedBmId) return;
        setAssigning(true);
        setAssignMessage(null);
        try {
            await apiClient.post(`/api/opportunities/${assignModal.opp.id}/assign-bid-manager`, {
                bid_manager_user_id: selectedBmId
            });
            setAssignMessage({ type: 'success', text: 'Bid Manager assigned successfully. Opportunity is now ACTIVE.' });
            await fetchOpportunities();
            setTimeout(() => {
                setAssignModal(null);
                setAssignMessage(null);
                setSelectedBmId('');
            }, 1500);
        } catch (err: any) {
            setAssignMessage({ type: 'error', text: err?.response?.data?.detail || 'Failed to assign Bid Manager.' });
        } finally {
            setAssigning(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'sync') {
            fetchSyncStatus();
            const interval = setInterval(fetchSyncStatus, 10000);
            return () => clearInterval(interval);
        } else if (activeTab === 'opportunities' || activeTab === 'opps-mgmt') {
            fetchOpportunities();
            if (activeTab === 'opportunities') fetchBMUsers();
        } else {
            fetchUsers();
        }
    }, [activeTab]);

    const handleForceSync = async () => {
        setIsSyncing(true);
        setSyncMessage({ type: 'info', text: 'Initiating Oracle CRM synchronization...' });
        try {
            const response = await apiClient.post(API_ENDPOINTS.BATCH_SYNC.START, {
                batch_size: 10,
                sync_name: "oracle_opportunities"
            });
            setSyncMessage({ type: 'success', text: response.data.message || 'Batch sync job started successfully.' });
            fetchSyncStatus();
        } catch (err: any) {
            setSyncMessage({ type: 'error', text: err?.response?.data?.detail || 'Failed to start synchronization.' });
        } finally {
            setIsSyncing(false);
        }
    };

    const handleResetSync = async () => {
        if (!window.confirm("Are you sure you want to reset the sync offset?")) return;
        try {
            await apiClient.post(API_ENDPOINTS.BATCH_SYNC.RESET);
            setSyncMessage({ type: 'success', text: 'Sync state reset successfully.' });
            fetchSyncStatus();
        } catch (err: any) {
            setSyncMessage({ type: 'error', text: 'Failed to reset sync state.' });
        }
    };

    const handleOpenModal = (userToEdit: User | null = null) => {
        if (userToEdit) {
            setEditingUser(userToEdit);
            setFormData(userToEdit);
        } else {
            setEditingUser(null);
            setFormData({
                email: '',
                display_name: '',
                roles: ['SA'],
                manager_email: '',
                geo_region: '',
                practice_name: '',
                is_active: true
            });
        }
        setIsModalOpen(true);
    };

    const handleSaveUser = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingUser) {
                await apiClient.put(`/api/admin/users/${editingUser.user_id}`, formData);
            } else {
                await apiClient.post('/api/admin/users/', formData);
            }
            setIsModalOpen(false);
            fetchUsers();
        } catch (err: any) {
            alert(err?.response?.data?.detail || "Failed to save user");
        }
    };

    const handleDeleteUser = async (user_id: string) => {
        if (!window.confirm("Are you sure you want to delete this user?")) return;
        try {
            await apiClient.delete(`/api/admin/users/${user_id}`);
            fetchUsers();
        } catch (err: any) {
            alert("Failed to delete user");
        }
    };

    if (!['GH', 'ADMIN'].includes(user?.role ?? '')) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-slate-50">
                <div className="text-center p-8 bg-white rounded-2xl shadow-sm border border-slate-200">
                    <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h1 className="text-xl font-bold text-slate-900">Access Denied</h1>
                    <p className="text-slate-500 mt-2">You do not have administrative privileges to access this page.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#f8fafc] p-6 md:p-10 font-[Outfit]">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">Admin Control Panel</h1>
                        <p className="text-slate-500 mt-1">Manage users, hierarchy, and CRM integration</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex bg-slate-200/50 p-1 rounded-xl">
                            <button
                                onClick={() => setActiveTab('users')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'users' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                User Management
                            </button>
                            <button
                                onClick={() => setActiveTab('opportunities')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'opportunities' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                Assign Bid Managers
                            </button>
                            <button
                                onClick={() => setActiveTab('opps-mgmt')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'opps-mgmt' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                Opportunities
                            </button>
                            <button
                                onClick={() => setActiveTab('sync')}
                                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'sync' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                Oracle CRM Sync
                            </button>
                        </div>
                        <div className="bg-indigo-50 p-3 rounded-2xl hidden sm:block">
                            <Settings className="w-8 h-8 text-indigo-600" />
                        </div>
                    </div>
                </div>

                {activeTab === 'opps-mgmt' ? (
                    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-50 flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-bold text-slate-800">All Opportunities</h2>
                                <p className="text-sm text-slate-400 mt-0.5">View and manage all bid opportunities across all statuses</p>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
                                {(['all', 'OPEN', 'ACTIVE', 'CLOSED', 'REOPENED'] as const).map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setOppMgmtFilter(f)}
                                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${oppMgmtFilter === f ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                                    >
                                        {f === 'all' ? 'All' : f}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {reopenMsg && (
                            <div className={`mx-6 mt-4 px-4 py-3 rounded-xl flex items-center justify-between text-sm font-medium ${reopenMsg.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                                <span>{reopenMsg.text}</span>
                                <button onClick={() => setReopenMsg(null)} className="ml-4 opacity-60 hover:opacity-100"><X className="w-4 h-4" /></button>
                            </div>
                        )}

                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-50/50 text-[10px] uppercase tracking-widest text-slate-400 font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Opportunity</th>
                                        <th className="px-6 py-4">Customer</th>
                                        <th className="px-6 py-4">Deal Value</th>
                                        <th className="px-6 py-4">Status</th>
                                        <th className="px-6 py-4">Assigned BM</th>
                                        <th className="px-6 py-4 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50">
                                    {isLoadingOpps ? (
                                        <tr><td colSpan={6} className="text-center py-10 text-slate-400">Loading opportunities...</td></tr>
                                    ) : (() => {
                                        const mgmtFiltered = opportunities.filter(o =>
                                            oppMgmtFilter === 'all' ? true : o.workflow_status === oppMgmtFilter
                                        );
                                        if (mgmtFiltered.length === 0) {
                                            return <tr><td colSpan={6} className="text-center py-10 text-slate-400">No opportunities found.</td></tr>;
                                        }
                                        return mgmtFiltered.map((opp: any) => (
                                            <tr key={opp.id} className="hover:bg-slate-50/30 transition-colors">
                                                <td className="px-6 py-4">
                                                    <div className="font-bold text-slate-900 max-w-[260px] truncate">{opp.name}</div>
                                                    <div className="text-xs text-slate-400 font-mono">#{opp.remote_id}</div>
                                                </td>
                                                <td className="px-6 py-4 text-sm text-slate-600">{opp.customer_name || opp.customer}</td>
                                                <td className="px-6 py-4 text-sm font-bold text-indigo-600">
                                                    {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', notation: 'compact' }).format(opp.deal_value)}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-full border ${
                                                        opp.workflow_status === 'OPEN' ? 'bg-sky-50 text-sky-600 border-sky-200' :
                                                        opp.workflow_status === 'ACTIVE' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                                                        opp.workflow_status === 'REOPENED' ? 'bg-amber-50 text-amber-600 border-amber-200' :
                                                        opp.workflow_status === 'CLOSED' ? 'bg-slate-100 text-slate-500 border-slate-200' :
                                                        'bg-slate-100 text-slate-500 border-slate-200'
                                                    }`}>
                                                        {opp.workflow_status === 'CLOSED' && <Lock className="w-2.5 h-2.5" />}
                                                        {opp.workflow_status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-sm">
                                                    {opp.bid_manager ? (
                                                        <span className="flex items-center gap-1.5 text-emerald-700 font-medium">
                                                            <UserCheck className="w-3.5 h-3.5" />
                                                            {opp.bid_manager}
                                                        </span>
                                                    ) : (
                                                        <span className="text-slate-300 italic text-xs">Unassigned</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    {opp.workflow_status === 'CLOSED' ? (
                                                        <button
                                                            onClick={() => handleReopen(opp)}
                                                            disabled={reopening === opp.id}
                                                            className="flex items-center gap-1.5 ml-auto px-3 py-1.5 text-xs font-bold rounded-lg border border-amber-300 text-amber-700 hover:bg-amber-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                                        >
                                                            {reopening === opp.id ? (
                                                                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                                            ) : (
                                                                <RotateCcw className="w-3.5 h-3.5" />
                                                            )}
                                                            {reopening === opp.id ? 'Reopening...' : 'Reopen'}
                                                        </button>
                                                    ) : (
                                                        <span className="text-xs text-slate-300 italic">—</span>
                                                    )}
                                                </td>
                                            </tr>
                                        ));
                                    })()}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ) : activeTab === 'opportunities' ? (
                    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-50 flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-bold text-slate-800">Bid Manager Assignment</h2>
                                <p className="text-sm text-slate-400 mt-0.5">Assign a Bid Manager to each opportunity to activate it</p>
                            </div>
                            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
                                {(['OPEN', 'ACTIVE', 'all'] as const).map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setOppStatusFilter(f)}
                                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${oppStatusFilter === f ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                                    >
                                        {f === 'all' ? 'All' : f}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-50/50 text-[10px] uppercase tracking-widest text-slate-400 font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Opportunity</th>
                                        <th className="px-6 py-4">Customer</th>
                                        <th className="px-6 py-4">Deal Value</th>
                                        <th className="px-6 py-4">Status</th>
                                        <th className="px-6 py-4">Assigned BM</th>
                                        <th className="px-6 py-4 text-right">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50">
                                    {isLoadingOpps ? (
                                        <tr><td colSpan={6} className="text-center py-10 text-slate-400">Loading opportunities...</td></tr>
                                    ) : (() => {
                                        const filtered = opportunities.filter(o =>
                                            oppStatusFilter === 'all' ? o.workflow_status !== 'CLOSED' :
                                            o.workflow_status === oppStatusFilter
                                        );
                                        if (filtered.length === 0) {
                                            return <tr><td colSpan={6} className="text-center py-10 text-slate-400">No opportunities found.</td></tr>;
                                        }
                                        return filtered.map((opp: any) => (
                                            <tr key={opp.id} className="hover:bg-slate-50/30 transition-colors">
                                                <td className="px-6 py-4">
                                                    <div className="font-bold text-slate-900 max-w-[260px] truncate">{opp.name}</div>
                                                    <div className="text-xs text-slate-400 font-mono">#{opp.remote_id}</div>
                                                </td>
                                                <td className="px-6 py-4 text-sm text-slate-600">{opp.customer_name || opp.customer}</td>
                                                <td className="px-6 py-4 text-sm font-bold text-indigo-600">
                                                    {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', notation: 'compact' }).format(opp.deal_value)}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${
                                                        opp.workflow_status === 'OPEN' ? 'bg-sky-50 text-sky-600 border-sky-200' :
                                                        opp.workflow_status === 'ACTIVE' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                                                        opp.workflow_status === 'REOPENED' ? 'bg-amber-50 text-amber-600 border-amber-200' :
                                                        'bg-slate-100 text-slate-500 border-slate-200'
                                                    }`}>
                                                        {opp.workflow_status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-sm">
                                                    {opp.bid_manager ? (
                                                        <span className="flex items-center gap-1.5 text-emerald-700 font-medium">
                                                            <UserCheck className="w-3.5 h-3.5" />
                                                            {opp.bid_manager}
                                                        </span>
                                                    ) : (
                                                        <span className="text-slate-300 italic text-xs">Unassigned</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    <button
                                                        onClick={() => { setAssignModal({ opp }); setSelectedBmId(opp.bid_manager_user_id || ''); setAssignMessage(null); }}
                                                        className="flex items-center gap-1.5 ml-auto px-3 py-1.5 text-xs font-bold rounded-lg border border-indigo-200 text-indigo-600 hover:bg-indigo-50 transition-all"
                                                    >
                                                        <UserCheck className="w-3.5 h-3.5" />
                                                        {opp.bid_manager ? 'Reassign BM' : 'Assign BM'}
                                                    </button>
                                                </td>
                                            </tr>
                                        ));
                                    })()}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ) : activeTab === 'users' ? (
                    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-50 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-slate-800">Organizational Hierarchy</h2>
                            <button 
                                onClick={() => handleOpenModal()}
                                className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100"
                            >
                                <UserPlus className="w-4 h-4" />
                                Add User
                            </button>
                        </div>
                        
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-50/50 text-[10px] uppercase tracking-widest text-slate-400 font-bold">
                                    <tr>
                                        <th className="px-6 py-4">User Details</th>
                                        <th className="px-6 py-4">Roles</th>
                                        <th className="px-6 py-4">Manager</th>
                                        <th className="px-6 py-4">Geo / Practice</th>
                                        <th className="px-6 py-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50">
                                    {isLoadingUsers ? (
                                        <tr><td colSpan={5} className="text-center py-10 text-slate-400">Loading user directory...</td></tr>
                                    ) : users.length === 0 ? (
                                        <tr><td colSpan={5} className="text-center py-10 text-slate-400">No users found.</td></tr>
                                    ) : users.map(u => (
                                        <tr key={u.user_id} className="hover:bg-slate-50/30 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="font-bold text-slate-900">{u.display_name}</div>
                                                <div className="text-xs text-slate-400 font-mono">{u.email}</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {u.roles.map(r => (
                                                        <span key={r} className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[10px] font-bold">
                                                            {r}
                                                        </span>
                                                    ))}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-sm text-slate-600">{u.manager_email || <span className="text-slate-300 italic">Unassigned</span>}</div>
                                            </td>
                                            <td className="px-6 py-4 text-sm">
                                                <div className="flex items-center gap-1.5 text-slate-600 mb-1">
                                                    <Globe className="w-3 h-3 text-slate-300" />
                                                    {u.geo_region || '-'}
                                                </div>
                                                <div className="flex items-center gap-1.5 text-slate-600">
                                                    <Briefcase className="w-3 h-3 text-slate-300" />
                                                    {u.practice_name || '-'}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex justify-end gap-2">
                                                    <button 
                                                        onClick={() => handleOpenModal(u)}
                                                        className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                                        title="Edit User"
                                                    >
                                                        <Edit2 className="w-4 h-4" />
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDeleteUser(u.user_id)}
                                                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                                        title="Delete User"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ) : (
                    <div className="grid gap-6">
                        <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm transition-all hover:shadow-md">
                            <div className="flex items-start justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="bg-blue-50 p-3 rounded-xl">
                                        <Database className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold text-slate-800">Oracle CRM Synchronization</h2>
                                        <p className="text-sm text-slate-400">Manage data flow between Oracle and BQS</p>
                                    </div>
                                </div>
                                {syncStatus?.is_complete === false && (
                                    <div className="flex items-center gap-2 bg-amber-50 text-amber-600 px-3 py-1 rounded-full text-xs font-bold animate-pulse">
                                        <RefreshCw className="w-3 h-3 animate-spin" />
                                        SYNC IN PROGRESS
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                                    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Processed</span>
                                    <p className="text-2xl font-bold text-slate-800">{syncStatus?.total_synced || 0}</p>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                                    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">In DB</span>
                                    <p className="text-2xl font-bold text-slate-800">{syncStatus?.total_in_db || 0}</p>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                                    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Offset</span>
                                    <p className="text-2xl font-bold text-slate-800">{syncStatus?.current_offset || 0}</p>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                                    <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Status</span>
                                    <p className={`text-sm font-bold mt-2 ${syncStatus?.is_complete ? 'text-emerald-600' : 'text-amber-600'}`}>
                                        {syncStatus?.is_complete ? 'COMPLETED' : (syncStatus?.current_offset > 0 ? 'PARTIAL' : 'NOT STARTED')}
                                    </p>
                                </div>
                            </div>

                            {syncMessage && (
                                <div className={`mb-6 p-4 rounded-2xl flex items-center gap-3 border ${
                                    syncMessage.type === 'success' ? 'bg-emerald-50 border-emerald-100 text-emerald-800' :
                                    syncMessage.type === 'error' ? 'bg-red-50 border-red-100 text-red-800' :
                                    'bg-blue-50 border-blue-100 text-blue-800'
                                }`}>
                                    {syncMessage.type === 'success' ? <CheckCircle className="w-5 h-5 shrink-0" /> : <AlertCircle className="w-5 h-5 shrink-0" />}
                                    <p className="text-sm font-medium">{syncMessage.text}</p>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-4">
                                <button
                                    onClick={handleForceSync}
                                    disabled={isSyncing}
                                    className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-bold tracking-tight transition-all active:scale-95 ${
                                        isSyncing ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-200'
                                    }`}
                                >
                                    <RefreshCw className={`w-5 h-5 ${isSyncing ? 'animate-spin' : ''}`} />
                                    {isSyncing ? 'Starting Sync...' : 'Force CRM Sync'}
                                </button>
                                <button onClick={handleResetSync} className="flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-all active:scale-95">
                                    <Terminal className="w-5 h-5" />
                                    Reset Offset
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Assign BM Modal */}
            {assignModal && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-[32px] w-full max-w-md shadow-2xl relative animate-in fade-in zoom-in duration-200">
                        <button
                            onClick={() => { setAssignModal(null); setAssignMessage(null); setSelectedBmId(''); }}
                            className="absolute top-6 right-6 p-2 h-10 w-10 flex items-center justify-center rounded-2xl text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-all"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <div className="p-10">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="bg-indigo-50 p-2.5 rounded-xl">
                                    <UserCheck className="w-5 h-5 text-indigo-600" />
                                </div>
                                <h3 className="text-2xl font-bold text-slate-900">
                                    {assignModal.opp.bid_manager ? 'Reassign Bid Manager' : 'Assign Bid Manager'}
                                </h3>
                            </div>
                            <p className="text-slate-400 text-sm mb-6 ml-1">
                                Opportunity will transition to <span className="font-bold text-indigo-600">ACTIVE</span> once a BM is assigned.
                            </p>

                            <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4 mb-6">
                                <div className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mb-1">Opportunity</div>
                                <div className="font-bold text-slate-800 truncate">{assignModal.opp.name}</div>
                                <div className="text-xs text-slate-500 mt-0.5">#{assignModal.opp.remote_id} · {assignModal.opp.customer_name || assignModal.opp.customer}</div>
                                {assignModal.opp.bid_manager && (
                                    <div className="mt-2 text-xs text-slate-500">
                                        Current BM: <span className="font-bold text-emerald-600">{assignModal.opp.bid_manager}</span>
                                    </div>
                                )}
                            </div>

                            <div className="space-y-1.5 mb-6">
                                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Select Bid Manager</label>
                                <div className="relative">
                                    <select
                                        value={selectedBmId}
                                        onChange={e => setSelectedBmId(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-4 pr-10 focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all appearance-none font-medium text-slate-800"
                                    >
                                        <option value="">— Select a Bid Manager —</option>
                                        {bmUsers.length === 0 ? (
                                            <option disabled>No BM users found</option>
                                        ) : bmUsers.map(bm => (
                                            <option key={bm.user_id} value={bm.user_id}>{bm.display_name}</option>
                                        ))}
                                    </select>
                                    <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                                </div>
                            </div>

                            {assignMessage && (
                                <div className={`mb-6 p-3 rounded-xl flex items-center gap-2 text-sm font-medium border ${
                                    assignMessage.type === 'success' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-red-50 text-red-700 border-red-100'
                                }`}>
                                    {assignMessage.type === 'success' ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
                                    {assignMessage.text}
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    onClick={() => { setAssignModal(null); setAssignMessage(null); setSelectedBmId(''); }}
                                    disabled={assigning}
                                    className="flex-1 px-6 py-3.5 rounded-2xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-all disabled:opacity-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleAssignBM}
                                    disabled={assigning || !selectedBmId}
                                    className="flex-[2] px-6 py-3.5 rounded-2xl font-bold bg-indigo-600 text-white hover:bg-indigo-700 shadow-xl shadow-indigo-100 flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {assigning ? (
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    ) : (
                                        <UserCheck className="w-4 h-4" />
                                    )}
                                    {assigning ? 'Assigning...' : 'Confirm Assignment'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Add/Edit Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-[32px] w-full max-w-lg shadow-2xl relative animate-in fade-in zoom-in duration-200">
                        <button 
                            onClick={() => setIsModalOpen(false)}
                            className="absolute top-6 right-6 p-2 h-10 w-10 flex items-center justify-center rounded-2xl text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-all"
                        >
                            <X className="w-6 h-6" />
                        </button>

                        <form onSubmit={handleSaveUser} className="p-10">
                            <h3 className="text-2xl font-bold text-slate-900 mb-2">{editingUser ? 'Edit System User' : 'Provision New User'}</h3>
                            <p className="text-slate-400 text-sm mb-8">Set up account details and organizational reporting lines.</p>

                            <div className="space-y-6">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5 col-span-2">
                                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Display Name</label>
                                        <input 
                                            type="text" 
                                            required
                                            value={formData.display_name}
                                            onChange={e => setFormData({...formData, display_name: e.target.value})}
                                            className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-4 focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all"
                                            placeholder="John Doe"
                                        />
                                    </div>
                                    <div className="space-y-1.5 col-span-2">
                                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Email Address</label>
                                        <input 
                                            type="email" 
                                            required
                                            disabled={!!editingUser}
                                            value={formData.email}
                                            onChange={e => setFormData({...formData, email: e.target.value})}
                                            className={`w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-4 focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all ${editingUser ? 'opacity-50 cursor-not-allowed' : ''}`}
                                            placeholder="john.doe@company.com"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Manager Email</label>
                                        <input 
                                            type="email" 
                                            value={formData.manager_email}
                                            onChange={e => setFormData({...formData, manager_email: e.target.value})}
                                            className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all"
                                            placeholder="boss@company.com"
                                        />
                                    </div>
                                    <div className="space-y-1.5 text-center flex flex-col justify-end">
                                         <label className="flex items-center gap-2 cursor-pointer p-4 bg-slate-50 rounded-2xl border border-slate-100 hover:bg-slate-100 transition-all">
                                            <input 
                                                type="checkbox" 
                                                checked={formData.is_active}
                                                onChange={e => setFormData({...formData, is_active: e.target.checked})}
                                                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500"
                                            />
                                            <span className="text-sm font-bold text-slate-600">Active Account</span>
                                         </label>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Geography / Region</label>
                                        <input 
                                            type="text" 
                                            value={formData.geo_region}
                                            onChange={e => setFormData({...formData, geo_region: e.target.value})}
                                            className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all"
                                            placeholder="Americas, EMEA, etc."
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Practice Unit</label>
                                        <input 
                                            type="text" 
                                            value={formData.practice_name}
                                            onChange={e => setFormData({...formData, practice_name: e.target.value})}
                                            className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all"
                                            placeholder="Cloud, LegalTech, etc."
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Assign Roles (Comma separated)</label>
                                    <input 
                                        type="text" 
                                        required
                                        value={formData.roles?.join(', ')}
                                        onChange={e => setFormData({...formData, roles: e.target.value.split(',').map(s => s.trim()).filter(s => s !== '')})}
                                        className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-3 text-sm focus:outline-none focus:ring-4 focus:ring-indigo-50 focus:border-indigo-200 transition-all"
                                        placeholder="GH, PH, SA, SH, etc."
                                    />
                                    <p className="text-[10px] text-slate-400 mt-1 italic">Valid Roles: GH, PH, SA, SH, SP, LEGAL, FINANCE, BID_MANAGER</p>
                                </div>
                            </div>

                            <div className="mt-10 flex gap-4">
                                <button 
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 px-8 py-4 rounded-2xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-all"
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="submit"
                                    className="flex-3 px-12 py-4 rounded-2xl font-bold bg-indigo-600 text-white hover:bg-indigo-700 shadow-xl shadow-indigo-100 flex items-center justify-center gap-2 transition-all active:scale-95"
                                >
                                    <Save className="w-5 h-5" />
                                    {editingUser ? 'Update User' : 'Create User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;
