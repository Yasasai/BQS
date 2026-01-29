import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, Home, Bell, User, LayoutDashboard, Inbox, CheckSquare } from 'lucide-react';

export function TopBar() {
    const navigate = useNavigate();

    return (
        <header className="bg-[#FDF3E1] border-b border-gray-200 h-14 flex items-center justify-between px-6 sticky top-0 z-50">
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-4">
                    <Menu size={20} className="text-gray-600 cursor-pointer" />
                    <div className="flex items-center gap-3">
                        <span className="text-[#5B5B5B] text-2xl font-normal tracking-tight" style={{ fontFamily: '"Libre Baskerville", serif' }}>inspira</span>
                        <div className="h-10 w-10 bg-[#C62828] flex flex-col items-center justify-center p-1 leading-none text-[6px] font-bold text-white text-center rounded-sm">
                            <div className="text-[4px]">Great</div>
                            <div className="text-[4px]">Place</div>
                            <div className="text-[4px]">To</div>
                            <div className="text-[4px]">Work</div>
                            <div className="text-[3px] opacity-70 mt-0.5">Certified</div>
                        </div>
                    </div>
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

            <div className="flex items-center gap-6 pr-4">
                <Search size={22} className="text-[#5B5B5B] cursor-pointer hover:text-blue-600" />
                <div className="relative">
                    <Bell size={22} className="text-[#5B5B5B] cursor-pointer" />
                    <span className="absolute -top-1.5 -right-1.5 bg-[#C62828] text-white text-[9px] rounded-full h-4 w-4 flex items-center justify-center font-bold border-2 border-[#FDF3E1]">1</span>
                </div>
                <div className="text-[#5B5B5B] cursor-pointer hover:text-blue-600">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                </div>
                <div className="text-[#5B5B5B] cursor-pointer hover:text-blue-600">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <User size={28} className="text-[#5B5B5B] cursor-pointer" />
            </div>
        </header>
    );
}
