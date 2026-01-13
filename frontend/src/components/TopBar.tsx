import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Home, Bell, User, LayoutDashboard, Inbox, CheckSquare } from 'lucide-react';

export function TopBar() {
    const navigate = useNavigate();

    return (
        <header className="bg-white border-b border-gray-200 h-12 flex items-center justify-between px-4 sticky top-0 z-50">
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                    <Menu size={20} className="text-gray-500 cursor-pointer" />
                    <span className="text-[#003366] text-xl font-serif italic tracking-tighter">inspira</span>
                </div>

                <nav className="flex items-center gap-4 ml-6">
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-1.5 text-xs font-medium text-gray-600 hover:text-blue-600"
                    >
                        <Inbox size={14} />
                        Opportunity Inbox
                    </button>
                    <button
                        onClick={() => navigate('/assigned-to-me')}
                        className="flex items-center gap-1.5 text-xs font-medium text-gray-600 hover:text-blue-600"
                    >
                        <CheckSquare size={14} />
                        Assigned to Me
                    </button>
                </nav>
            </div>

            <div className="flex items-center gap-4">
                <Home size={18} className="text-gray-500 cursor-pointer hover:text-blue-600" onClick={() => navigate('/')} />
                <div className="relative">
                    <Bell size={18} className="text-gray-500 cursor-pointer" />
                    <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-[9px] rounded-full h-3 w-3 flex items-center justify-center font-bold">3</span>
                </div>
                <div className="flex items-center justify-center w-7 h-7 bg-orange-100 rounded-full text-orange-700 text-[10px] font-bold border border-orange-200">
                    YU
                </div>
            </div>
        </header>
    );
}
