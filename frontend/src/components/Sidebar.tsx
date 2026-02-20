import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Inbox, User, LogOut, LayoutDashboard, FileText, CheckCircle, AlertCircle, PlayCircle, ChevronUp, ChevronDown, GripHorizontal } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useAuth } from '../context/AuthContext';

export function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const { availableUsers, switchUser } = useUser();
    const { user, login } = useAuth();

    // Resizable slider state
    const [sliderHeight, setSliderHeight] = useState(250);
    const isResizing = useRef(false);

    const startResizing = useCallback(() => {
        isResizing.current = true;
        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
    }, []);

    const stopResizing = useCallback(() => {
        isResizing.current = false;
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
    }, []);

    const resize = useCallback((e: MouseEvent) => {
        if (!isResizing.current) return;
        const newHeight = window.innerHeight - e.clientY - 80; // Subtract profile height
        if (newHeight > 100 && newHeight < 600) {
            setSliderHeight(newHeight);
        }
    }, []);

    useEffect(() => {
        window.addEventListener('mousemove', resize);
        window.addEventListener('mouseup', stopResizing);
        return () => {
            window.removeEventListener('mousemove', resize);
            window.removeEventListener('mouseup', stopResizing);
        };
    }, [resize, stopResizing]);

    if (!user) return null;

    const isPathActive = (path: string) => location.pathname === path;

    const handleUserSwitch = (u: any) => {
        switchUser(u.user_id);
        const roles = (u.roles || []).map((r: string) => r.toUpperCase());
        let targetRole: 'GH' | 'PH' | 'SH' | 'SA' | 'SP' = 'SA';

        if (roles.includes("MANAGEMENT") || roles.includes("GH") || roles.includes("GLOBAL_HEAD")) targetRole = 'GH';
        else if (roles.includes("PRACTICE_HEAD") || roles.includes("PH")) targetRole = 'PH';
        else if (roles.includes("SALES_HEAD") || roles.includes("SH") || roles.includes("SALES_LEAD")) targetRole = 'SH';
        else if (roles.includes("SALES_PERSON") || roles.includes("SP") || roles.includes("SALES_REPRESENTATIVE")) targetRole = 'SP';
        else if (roles.includes("SOLUTION_ARCHITECT") || roles.includes("SA")) targetRole = 'SA';

        login(targetRole, {
            id: u.user_id,
            email: u.email,
            name: u.display_name,
            role: targetRole,
            displayRole: targetRole === 'GH' ? 'Global Head' :
                targetRole === 'PH' ? 'Practice Head' :
                    targetRole === 'SH' ? 'Sales Head' :
                        targetRole === 'SP' ? 'Sales Representative' : 'Solution Architect'
        });

        if (targetRole === 'GH') navigate('/management/all');
        else if (targetRole === 'PH') navigate('/practice-head/dashboard');
        else if (targetRole === 'SH') navigate('/sales/action-required');
        else if (targetRole === 'SA' || targetRole === 'SP') navigate('/assigned-to-me');
    };

    return (
        <div className="w-80 h-screen bg-[#f8f8f8] border-r border-[#e1e1e1] flex flex-col shadow-none flex-shrink-0">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[#e1e1e1] flex items-center gap-2 bg-white">
                <div className="bg-[#5c5c5c] text-white px-1.5 py-0.5 rounded-sm font-bold text-xs">BQS</div>
                <span className="font-bold text-[#5c5c5c] tracking-tight">Bid Scale</span>
            </div>

            {/* Main Nav */}
            <div className="flex-1 py-4 space-y-0.5 overflow-y-auto bg-white">
                <div onClick={() => navigate('/')} className={`flex items-center gap-3 px-6 py-2 cursor-pointer ${isPathActive('/') ? 'bg-white text-black font-bold border-r-4 border-[#5c5c5c]' : 'text-gray-600 hover:bg-gray-100'}`}>
                    <Home size={18} />
                    <span className="text-sm">Home</span>
                </div>

                {/* GH Navigation */}
                {user.role === 'GH' && (
                    <>
                        <div className="px-6 pt-4 pb-1 text-[10px] font-bold text-gray-400 uppercase">Management</div>
                        <div onClick={() => navigate('/management/dashboard')} className={`flex items-center gap-3 px-6 py-2 cursor-pointer ${isPathActive('/management/dashboard') ? 'bg-white text-black font-bold border-r-4 border-[#5c5c5c]' : 'text-gray-600 hover:bg-gray-100'}`}>
                            <LayoutDashboard size={18} />
                            <span className="text-sm">Dashboard</span>
                        </div>
                    </>
                )}

                {/* Sales Head Navigation */}
                {user.role === 'SH' && (
                    <>
                        <div className="px-6 pt-4 pb-1 text-[10px] font-bold text-gray-400 uppercase">Sales Head</div>
                        <div onClick={() => navigate('/sales/action-required')} className={`flex items-center gap-3 px-6 py-2 cursor-pointer ${isPathActive('/sales/action-required') ? 'bg-white text-black font-bold border-r-4 border-[#5c5c5c]' : 'text-gray-600 hover:bg-gray-100'}`}>
                            <AlertCircle size={18} />
                            <span className="text-sm">Action Required</span>
                        </div>
                    </>
                )}

                {/* PH Navigation */}
                {user.role === 'PH' && (
                    <>
                        <div className="px-6 pt-4 pb-1 text-[10px] font-bold text-gray-400 uppercase">Practice Head</div>
                        <div onClick={() => navigate('/practice-head/dashboard')} className={`flex items-center gap-3 px-6 py-2 cursor-pointer ${isPathActive('/practice-head/dashboard') ? 'bg-white text-black font-bold border-r-4 border-[#5c5c5c]' : 'text-gray-600 hover:bg-gray-100'}`}>
                            <LayoutDashboard size={18} />
                            <span className="text-sm">Dashboard</span>
                        </div>
                    </>
                )}

                {/* SA Navigation */}
                {(user.role === 'SA' || user.role === 'SP') && (
                    <>
                        <div className="px-6 pt-4 pb-1 text-[10px] font-bold text-gray-400 uppercase">Assignments</div>
                        <div onClick={() => navigate('/assigned-to-me')} className={`flex items-center gap-3 px-6 py-2 cursor-pointer ${isPathActive('/assigned-to-me') ? 'bg-white text-black font-bold border-r-4 border-[#5c5c5c]' : 'text-gray-600 hover:bg-gray-100'}`}>
                            <Inbox size={18} />
                            <span className="text-sm">My Tasks</span>
                        </div>
                    </>
                )}
            </div>

            {/* Adjustable Splitter Handle */}
            <div
                className="h-1 bg-[#e1e1e1] hover:bg-gray-400 cursor-ns-resize flex items-center justify-center transition-colors group"
                onMouseDown={startResizing}
            >
            </div>

            {/* Demo User Switcher (Resizable) */}
            <div className="bg-[#f0f0f0] overflow-y-auto border-t border-[#e1e1e1]" style={{ height: `${sliderHeight}px` }}>
                <div className="p-4 pt-2">
                    <div className="text-[10px] text-gray-400 font-bold uppercase mb-2 sticky top-0 bg-[#f0f0f0] z-10 pb-1 border-b border-gray-200 flex justify-between items-center">
                        <span>Simulate User</span>
                    </div>
                    <div className="space-y-3">
                        {(() => {
                            const grouped = {
                                'Management': [] as typeof availableUsers,
                                'Practice Heads': [] as typeof availableUsers,
                                'Sales Heads': [] as typeof availableUsers,
                                'Solution Architects': [] as typeof availableUsers,
                                'Sales Persons': [] as typeof availableUsers,
                                'Others': [] as typeof availableUsers
                            };

                            availableUsers.forEach(u => {
                                const roles = (u.roles || []).map((r: string) => r.toUpperCase());
                                if (roles.includes('GH') || roles.includes('MANAGEMENT') || roles.includes('GLOBAL_HEAD')) grouped['Management'].push(u);
                                else if (roles.includes('PH') || roles.includes('PRACTICE_HEAD')) grouped['Practice Heads'].push(u);
                                else if (roles.includes('SH') || roles.includes('SALES_HEAD') || roles.includes('SALES_LEAD')) grouped['Sales Heads'].push(u);
                                else if (roles.includes('SA') || roles.includes('SOLUTION_ARCHITECT')) grouped['Solution Architects'].push(u);
                                else if (roles.includes('SP') || roles.includes('SALES_PERSON') || roles.includes('SALES_REPRESENTATIVE')) grouped['Sales Persons'].push(u);
                                else grouped['Others'].push(u);
                            });

                            return Object.entries(grouped).map(([category, users]) => {
                                if (users.length === 0) return null;
                                return (
                                    <div key={category}>
                                        <div className="text-[9px] font-bold text-gray-400 uppercase tracking-tighter mb-1 px-1">{category}</div>
                                        <div className="space-y-0.5">
                                            {users.map(u => (
                                                <button
                                                    key={u.user_id}
                                                    onClick={() => handleUserSwitch(u)}
                                                    className={`w-full text-left px-2 py-1 text-[11px] rounded transition-colors ${user.id === u.user_id
                                                        ? 'bg-white text-black font-bold border border-[#e1e1e1]'
                                                        : 'text-gray-600 hover:bg-gray-200'}`}
                                                >
                                                    <div className="truncate">{u.display_name}</div>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            });
                        })()}
                    </div>
                </div>
            </div>

            {/* Current User Profile */}
            <div className="p-4 border-t border-[#e1e1e1] flex items-center gap-3 bg-white">
                <div className="w-8 h-8 rounded bg-gray-200 flex items-center justify-center">
                    <User size={18} className="text-gray-500" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="text-[11px] font-bold text-gray-900 truncate">{user.name}</div>
                    <div className="text-[10px] text-gray-500 truncate lowercase italic">{user.displayRole}</div>
                </div>
            </div>
        </div>
    );
}
