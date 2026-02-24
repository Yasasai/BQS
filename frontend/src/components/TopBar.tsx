import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth, UserRole } from '../context/AuthContext';
import { Bell, ChevronDown, User, LogOut, Settings, LayoutGrid } from 'lucide-react';

const ROLES: { code: UserRole; label: string; name: string }[] = [
    { code: 'GH', label: 'Global Head', name: 'James Wilson' },
    { code: 'PH', label: 'Practice Head', name: 'Sarah Mitchell' },
    { code: 'SH', label: 'Sales Head', name: 'Robert Chen' },
    { code: 'SA', label: 'Solution Architect', name: 'John Doe' },
    { code: 'SP', label: 'Sales Representative', name: 'Emily White' },
];

export function TopBar() {
    const navigate = useNavigate();
    const { user, login, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const handleRoleSwitch = (role: UserRole) => {
        login(role);
        setIsMenuOpen(false);
        if (role === 'SA' || role === 'SP') {
            navigate('/assigned-to-me');
        } else if (role === 'GH') {
            navigate('/management/dashboard');
        } else if (role === 'SH') {
            navigate('/sales/dashboard');
        } else if (role === 'PH') {
            navigate('/practice-head/dashboard');
        } else {
            navigate('/');
        }
    };

    const currentUserRole = ROLES.find(r => r.code === user?.role) || ROLES[0];

    return (
        <header className="h-14 oracle-banner flex items-center justify-between px-6 sticky top-0 z-40">
            <div className="flex items-center gap-6">
                <Link to="/" className="flex items-center gap-2">
                    <span className="text-2xl font-light text-[#5c5c5c] tracking-tight">inspira</span>
                </Link>

                <nav className="hidden md:flex items-center gap-1">
                    <Link to="/" className="px-3 py-1 text-sm font-medium text-gray-700 hover:text-black">Home</Link>
                    <Link to="/opportunity-inbox" className="px-3 py-1 text-sm font-medium text-gray-700 hover:text-black">Marketplace</Link>
                    <Link to="/reports" className="px-3 py-1 text-sm font-medium text-gray-700 hover:text-black">Analytics</Link>
                </nav>
            </div>

            <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                    <button className="p-2 text-gray-600 hover:bg-black/5 rounded-full transition-all">
                        <Bell size={20} />
                    </button>
                    <button className="p-2 text-gray-600 hover:bg-black/5 rounded-full transition-all">
                        <LayoutGrid size={20} />
                    </button>
                </div>

                <div className="relative">
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="flex items-center gap-2 p-1 pl-3 hover:bg-black/5 rounded transition-all"
                    >
                        <div className="text-right hidden lg:block">
                            <p className="text-xs font-semibold text-gray-800 leading-none">{user?.name || currentUserRole.name}</p>
                            <p className="text-[10px] text-gray-500 uppercase font-bold mt-0.5">{user?.displayRole || currentUserRole.label}</p>
                        </div>
                        <div className="w-8 h-8 rounded-md bg-gray-300 border border-gray-400 overflow-hidden">
                            <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || currentUserRole.name)}&background=f0ebd8&color=333`} alt="user" />
                        </div>
                        <ChevronDown size={12} className={`text-gray-600 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {isMenuOpen && (
                        <div className="absolute right-0 mt-1 w-64 bg-white rounded shadow-lg border border-gray-200 py-2 z-50">
                            <div className="px-4 py-2 border-b border-gray-100 mb-1">
                                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Switch Role</p>
                            </div>
                            {ROLES.map((r) => (
                                <button
                                    key={r.code}
                                    onClick={() => handleRoleSwitch(r.code)}
                                    className={`w-full text-left px-4 py-2 text-sm ${user?.role === r.code ? 'bg-[#f0ebd8] font-bold' : 'hover:bg-gray-50 text-gray-700'}`}
                                >
                                    {r.label}
                                </button>
                            ))}
                            <div className="border-t border-gray-100 mt-2 pt-2">
                                <button onClick={() => logout()} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
