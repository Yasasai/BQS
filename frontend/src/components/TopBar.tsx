import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth, UserRole } from '../context/AuthContext';
import { Bell, ChevronDown, User, LogOut, Settings, LayoutGrid } from 'lucide-react';

const ROLES: { code: UserRole; label: string; name: string }[] = [
    { code: 'GH', label: 'Global Head', name: 'James Wilson' },
    { code: 'PH', label: 'Practice Head', name: 'Sarah Mitchell' },
    { code: 'SH', label: 'Sales Head', name: 'Robert Chen' },
    { code: 'SA', label: 'Solution Architect', name: 'John Doe' },
    { code: 'SP', label: 'Sales Presales', name: 'Emily White' },
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
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-40 shadow-sm">
            <div className="flex items-center gap-8">
                <Link to="/" className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-[#0572CE] rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/20">B</div>
                    <span className="text-xl font-black text-gray-900 tracking-tight">BQS <span className="text-blue-600">Enterprise</span></span>
                </Link>

                <nav className="hidden md:flex items-center gap-1">
                    <Link to="/" className="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">Home</Link>
                    <Link to="/opportunity-inbox" className="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">Marketplace</Link>
                    <Link to="/reports" className="px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">Analytics</Link>
                </nav>
            </div>

            <div className="flex items-center gap-4">
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-xl transition-all relative">
                    <Bell size={20} />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
                </button>

                <div className="h-8 w-[1px] bg-gray-100 mx-2" />

                <div className="relative">
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="flex items-center gap-3 p-1.5 pr-3 hover:bg-gray-50 rounded-xl transition-all border border-transparent hover:border-gray-200"
                    >
                        <div className="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center font-bold text-sm">
                            {currentUserRole.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="text-left hidden lg:block">
                            <p className="text-sm font-bold text-gray-900 leading-none">{currentUserRole.name}</p>
                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-1">{currentUserRole.label}</p>
                        </div>
                        <ChevronDown size={14} className={`text-gray-400 transition-transform duration-200 ${isMenuOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {isMenuOpen && (
                        <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 py-3 z-50 animate-in fade-in slide-in-from-top-2">
                            <div className="px-4 py-2 mb-2">
                                <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-3">Impersonate Role</p>
                                <div className="grid grid-cols-1 gap-1">
                                    {ROLES.map((r) => (
                                        <button
                                            key={r.code}
                                            onClick={() => handleRoleSwitch(r.code)}
                                            className={`flex items-center justify-between px-4 py-2.5 rounded-xl transition-all ${user?.role === r.code
                                                ? 'bg-blue-50 text-blue-700 shadow-sm'
                                                : 'hover:bg-gray-50 text-gray-600'
                                                }`}
                                        >
                                            <div className="flex flex-col items-start">
                                                <span className="text-sm font-bold">{r.label}</span>
                                                <span className="text-[10px] opacity-60 font-medium">{r.name}</span>
                                            </div>
                                            {user?.role === r.code && <div className="w-2 h-2 bg-blue-600 rounded-full" />}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="border-t border-gray-100 mt-2 pt-2">
                                <button className="w-full flex items-center gap-3 px-6 py-3 text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors">
                                    <Settings size={18} /> Settings
                                </button>
                                <button onClick={() => logout()} className="w-full flex items-center gap-3 px-6 py-3 text-sm font-bold text-red-600 hover:bg-red-50 transition-colors">
                                    <LogOut size={18} /> Sign Out
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
