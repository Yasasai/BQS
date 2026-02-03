import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Home, Bell, User, LayoutDashboard, Inbox, CheckSquare, Search, ChevronDown, UserCircle } from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';

export function TopBar() {
    const navigate = useNavigate();
    const { user, login } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const handleRoleSwitch = (role: UserRole) => {
        login(role);
        setIsMenuOpen(false);
        if (role === 'SOLUTION_ARCHITECT') {
            navigate('/assigned-to-me');
        } else {
            navigate('/');
        }
    };

    return (
        <header className="bg-white border-b border-[#E5E7EB] h-16 flex items-center justify-between px-8 sticky top-0 z-50 shadow-sm">
            <div className="flex items-center gap-8">
                <div className="flex items-center gap-6">
                    <Menu size={20} className="text-[#6B7280] cursor-pointer hover:text-[#111827]" />
                    <div className="flex items-center gap-3">
                        <span className="text-[#111827] text-2xl font-bold tracking-tight">inspira</span>
                        <div className="h-10 w-10 bg-[#EF4444] flex flex-col items-center justify-center p-1 leading-none text-[6px] font-bold text-white text-center rounded-md">
                            <div className="text-[4px]">Great</div>
                            <div className="text-[4px]">Place</div>
                            <div className="text-[4px]">To</div>
                            <div className="text-[4px]">Work</div>
                            <div className="text-[3px] opacity-80 mt-0.5 uppercase">Certified</div>
                        </div>
                    </div>
                </div>

                <nav className="flex items-center gap-6 ml-4">
                    {user?.role === 'PRACTICE_HEAD' && (
                        <button
                            onClick={() => navigate('/')}
                            className={`flex items-center gap-2 text-sm font-semibold transition-colors ${user?.role === 'PRACTICE_HEAD' ? 'text-[#2563EB]' : 'text-[#4B5563] hover:text-[#111827]'}`}
                        >
                            <Inbox size={16} />
                            Pipeline
                        </button>
                    )}
                    <button
                        onClick={() => navigate('/assigned-to-me')}
                        className={`flex items-center gap-2 text-sm font-semibold transition-colors ${user?.role === 'SOLUTION_ARCHITECT' ? 'text-[#2563EB]' : 'text-[#4B5563] hover:text-[#111827]'}`}
                    >
                        <CheckSquare size={16} />
                        My Work
                    </button>
                </nav>
            </div>

            <div className="flex items-center gap-8 pr-4">
                <Search size={20} className="text-[#6B7280] cursor-pointer hover:text-[#2563EB] transition-colors" />
                <div className="relative cursor-pointer group">
                    <Bell size={20} className="text-[#6B7280] group-hover:text-[#2563EB] transition-colors" />
                    <span className="absolute -top-1.5 -right-1.5 bg-[#EF4444] text-white text-[10px] rounded-full h-4 w-4 flex items-center justify-center font-bold border-2 border-white">1</span>
                </div>

                {/* User Profile & Role Switcher */}
                <div className="relative">
                    <div
                        className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-1.5 rounded-lg transition-all"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                    >
                        <div className="flex flex-col items-end">
                            <span className="text-sm font-bold text-[#111827]">{user?.name || 'Guest User'}</span>
                            <span className="text-[10px] text-[#6B7280] font-semibold uppercase tracking-wider">{user?.role?.replace('_', ' ') || 'No Role'}</span>
                        </div>
                        <div className="h-9 w-9 rounded-full bg-[#F3F4F6] flex items-center justify-center text-[#6B7280] border border-[#E5E7EB]">
                            <UserCircle size={22} />
                        </div>
                        <ChevronDown size={14} className="text-[#9CA3AF]" />
                    </div>

                    {isMenuOpen && (
                        <div className="absolute right-0 mt-3 w-64 bg-white rounded-xl shadow-2xl border border-[#E5E7EB] py-2 z-50 overflow-hidden">
                            <div className="px-4 py-2 border-b border-gray-50">
                                <p className="text-[10px] font-bold text-[#9CA3AF] uppercase tracking-widest">Switch Identity</p>
                            </div>
                            <button
                                onClick={() => handleRoleSwitch('PRACTICE_HEAD')}
                                className="w-full text-left px-4 py-3 text-sm hover:bg-[#F9FAFB] flex items-center gap-3 transition-colors"
                            >
                                <div className={`w-2.5 h-2.5 rounded-full ${user?.role === 'PRACTICE_HEAD' ? 'bg-[#2563EB]' : 'bg-gray-200'}`}></div>
                                <div className="flex flex-col">
                                    <span className="font-semibold text-[#111827]">Practice Head</span>
                                    <span className="text-[11px] text-[#6B7280]">Sarah Mitchell</span>
                                </div>
                            </button>
                            <button
                                onClick={() => handleRoleSwitch('SOLUTION_ARCHITECT')}
                                className="w-full text-left px-4 py-3 text-sm hover:bg-[#F9FAFB] flex items-center gap-3 transition-colors"
                            >
                                <div className={`w-2.5 h-2.5 rounded-full ${user?.role === 'SOLUTION_ARCHITECT' ? 'bg-[#2563EB]' : 'bg-gray-200'}`}></div>
                                <div className="flex flex-col">
                                    <span className="font-semibold text-[#111827]">Solution Architect</span>
                                    <span className="text-[11px] text-[#6B7280]">John Doe</span>
                                </div>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
