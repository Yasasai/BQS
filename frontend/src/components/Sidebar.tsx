
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Inbox, User, LogOut } from 'lucide-react';
import { useUser } from '../context/UserContext';

export function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser, availableUsers, switchUser } = useUser();

    if (!currentUser) return null;

    const isPathActive = (path: string) => location.pathname === path;
    const isLead = currentUser.roles.includes("SALES_LEAD");
    const isSA = currentUser.roles.includes("SA");

    return (
        <div className="w-80 h-screen bg-white border-r border-gray-200 flex flex-col shadow-sm flex-shrink-0">
            {/* Header */}
            <div className="px-6 py-5 border-b border-gray-100 flex items-center gap-2">
                <div className="bg-blue-600 text-white p-1 rounded font-bold text-sm">BQS</div>
                <span className="font-semibold text-gray-800">Bid Scale</span>
            </div>

            {/* Main Nav */}
            <div className="flex-1 py-4 space-y-1">
                <div onClick={() => navigate('/')} className={`flex items-center gap-3 px-6 py-3 cursor-pointer ${isPathActive('/') ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}>
                    <Inbox size={20} />
                    <span className="font-medium">Opportunity Inbox</span>
                </div>
                {/* Add more links later */}
            </div>

            {/* Demo User Switcher */}
            <div className="border-t p-4 bg-gray-50">
                <div className="text-xs text-gray-500 font-bold uppercase mb-2">Simulate User (MVP)</div>
                <div className="space-y-2">
                    {availableUsers.map(u => (
                        <button
                            key={u.user_id}
                            onClick={() => switchUser(u.user_id)}
                            className={`w-full text-left px-3 py-2 text-sm rounded border ${currentUser.user_id === u.user_id ? 'bg-white border-blue-500 shadow-sm ring-1 ring-blue-500' : 'bg-gray-100 border-transparent hover:bg-white hover:border-gray-200'}`}
                        >
                            <div className="font-medium text-gray-900">{u.display_name}</div>
                            <div className="text-xs text-gray-500">{u.roles.join(", ")}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Current User Profile */}
            <div className="p-4 border-t flex items-center gap-3">
                <div className="bg-gray-200 rounded-full p-2">
                    <User size={20} className="text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">{currentUser.display_name}</div>
                    <div className="text-xs text-gray-500 truncate">{currentUser.email}</div>
                </div>
            </div>
        </div>
    );
}
