import React, { useEffect, useState } from 'react';
import { X, Plus, Edit2, Check, User } from 'lucide-react';

interface ManageUsersModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface User {
    user_id: str;
    email: string;
    display_name: string;
    roles: string[];
    is_active: boolean;
}

export const ManageUsersModal: React.FC<ManageUsersModalProps> = ({ isOpen, onClose }) => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [view, setView] = useState<'list' | 'add' | 'edit'>('list');

    // Form State
    const [formData, setFormData] = useState({
        email: '',
        display_name: '',
        role: 'SA' // Simple approach: one role for now
    });
    const [editId, setEditId] = useState<string | null>(null);

    useEffect(() => {
        if (isOpen) fetchUsers();
    }, [isOpen]);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/api/users/');
            const data = await res.json();
            setUsers(data);
        } catch (e) {
            console.error(e);
            alert("Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!formData.email || !formData.display_name) return;

        try {
            const body = {
                email: formData.email,
                display_name: formData.display_name,
                roles: [formData.role]
            };

            let url = 'http://127.0.0.1:8000/api/users/';
            let method = 'POST';

            if (view === 'edit' && editId) {
                url = `http://127.0.0.1:8000/api/users/${editId}`;
                method = 'PUT';
            }

            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!res.ok) throw new Error("Failed to save");

            await fetchUsers();
            setView('list');
            setFormData({ email: '', display_name: '', role: 'SA' });
            setEditId(null);
        } catch (e) {
            alert("Error saving user");
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
            <div className="bg-white rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col">
                <div className="flex justify-between items-center p-4 border-b">
                    <h2 className="text-lg font-semibold text-gray-800">Manage Users</h2>
                    <button onClick={onClose}><X size={20} className="text-gray-500 hover:text-gray-700" /></button>
                </div>

                <div className="p-4 flex-1 overflow-y-auto">
                    {view === 'list' ? (
                        <div>
                            <div className="flex justify-between mb-4">
                                <h3 className="text-sm font-medium text-gray-600">All Users</h3>
                                <button
                                    onClick={() => { setView('add'); setFormData({ email: '', display_name: '', role: 'SA' }); }}
                                    className="flex items-center gap-2 text-sm text-blue-600 font-medium hover:underline"
                                >
                                    <Plus size={16} /> Add User
                                </button>
                            </div>

                            {loading ? (
                                <div className="text-center py-8 text-gray-500">Loading...</div>
                            ) : (
                                <div className="space-y-2">
                                    {users.map(u => (
                                        <div key={u.user_id} className="flex justify-between items-center p-3 border rounded hover:bg-gray-50">
                                            <div>
                                                <div className="font-medium text-gray-900">{u.display_name}</div>
                                                <div className="text-xs text-gray-500">{u.email} • {u.roles.join(', ')}</div>
                                            </div>
                                            <button
                                                onClick={() => {
                                                    setEditId(u.user_id);
                                                    setFormData({
                                                        email: u.email,
                                                        display_name: u.display_name,
                                                        role: u.roles[0] || 'SA'
                                                    });
                                                    setView('edit');
                                                }}
                                                className="p-2 text-gray-400 hover:text-blue-600"
                                            >
                                                <Edit2 size={16} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div>
                            <h3 className="text-sm font-medium text-gray-600 mb-4">{view === 'add' ? 'Add New User' : 'Edit User'}</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-gray-700 mb-1">Display Name</label>
                                    <input
                                        className="w-full border rounded p-2 text-sm"
                                        value={formData.display_name}
                                        onChange={e => setFormData({ ...formData, display_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-700 mb-1">Email</label>
                                    <input
                                        className="w-full border rounded p-2 text-sm"
                                        value={formData.email}
                                        onChange={e => setFormData({ ...formData, email: e.target.value })}
                                        disabled={view === 'edit'}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-700 mb-1">Role</label>
                                    <select
                                        className="w-full border rounded p-2 text-sm"
                                        value={formData.role}
                                        onChange={e => setFormData({ ...formData, role: e.target.value })}
                                    >
                                        <option value="SA">Solution Architect</option>
                                        <option value="PRACTICE_HEAD">Practice Head</option>
                                        <option value="SALES_LEAD">Sales Lead</option>
                                    </select>
                                </div>
                            </div>
                            <div className="flex justify-end gap-2 mt-6">
                                <button
                                    onClick={() => setView('list')}
                                    className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSave}
                                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                                >
                                    Save
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
