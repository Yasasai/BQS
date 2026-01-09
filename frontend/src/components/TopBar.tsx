import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Home, Bell, User, Inbox, ClipboardCheck } from 'lucide-react';

export function TopBar() {
    const location = useLocation();

    return (
        <div className="h-14 bg-crm-header flex items-center px-4 justify-between border-b border-gray-200 sticky top-0 z-50">
            <div className="flex items-center gap-6">
                <button className="text-gray-700 p-1 hover:bg-black/5 rounded">
                    <Menu size={20} />
                </button>
                <div className="flex flex-col leading-none">
                    <span className="text-2xl font-light text-gray-700 tracking-wide font-serif">inspira</span>
                </div>

                {/* Navigation Links */}
                <nav className="flex items-center gap-2 ml-4">
                    <Link
                        to="/"
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors ${location.pathname === '/'
                                ? 'bg-blue-100 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-100'
                            }`}
                    >
                        <Inbox size={16} />
                        Opportunity Inbox
                    </Link>
                    <Link
                        to="/assigned-to-me"
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors ${location.pathname === '/assigned-to-me'
                                ? 'bg-blue-100 text-blue-700'
                                : 'text-gray-600 hover:bg-gray-100'
                            }`}
                    >
                        <ClipboardCheck size={16} />
                        Assigned to Me
                    </Link>
                </nav>
            </div>

            <div className="flex items-center gap-4 text-gray-700">
                <button className="p-2 hover:bg-black/5 rounded-full">
                    <Home size={20} />
                </button>
                <div className="relative p-2 hover:bg-black/5 rounded-full cursor-pointer">
                    <Bell size={20} />
                    <div className="absolute top-1.5 right-1.5 w-4 h-4 bg-orange-500 rounded-full text-[10px] text-white flex items-center justify-center font-bold border-2 border-crm-header">3</div>
                </div>
                <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-700 font-medium text-xs cursor-pointer">
                    YU
                </div>
            </div>
        </div>
    );
}
