import React, { useState, useEffect } from 'react';
import { RefreshCw, Database, Terminal, Settings, AlertCircle, CheckCircle, UserPlus, Edit2, Trash2, Globe, MapPin, Briefcase, X, Save } from 'lucide-react';
import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { useAuth } from '../context/AuthContext';
import { User } from '../types';

const AdminDashboard: React.FC = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState<'sync' | 'users'>('users');
    
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

    useEffect(() => {
        if (activeTab === 'sync') {
            fetchSyncStatus();
            const interval = setInterval(fetchSyncStatus, 10000);
            return () => clearInterval(interval);
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

    if (user?.role !== 'GH') {
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

                {activeTab === 'users' ? (
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
