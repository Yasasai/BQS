import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Home, Inbox, UserCheck, BarChart3, FileCheck,
    ChevronDown, ArrowLeft, Briefcase, Target, Award
} from 'lucide-react';
import { useUser } from '../context/UserContext';

interface SidebarItemProps {
    label: string;
    icon?: React.ElementType;
    hasSubmenu?: boolean;
    isActive?: boolean;
    onClick?: () => void;
    path?: string;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ label, icon: Icon, hasSubmenu, isActive, onClick, path }) => {
    return (
        <div
            onClick={onClick}
            className={`flex items-center justify-between px-4 py-3 cursor-pointer transition-colors ${isActive
                ? 'bg-orange-50 text-orange-600 border-l-4 border-orange-500'
                : 'text-gray-700 hover:bg-gray-50 border-l-4 border-transparent'
                }`}
        >
            <div className="flex items-center gap-3">
                {Icon && <Icon size={20} className={isActive ? 'text-orange-500' : 'text-gray-500'} />}
                <span className={`text-sm font-medium ${isActive ? 'text-orange-900' : 'text-gray-700'}`}>
                    {label}
                </span>
            </div>
            {hasSubmenu && <ChevronDown size={16} className="text-gray-400" />}
        </div>
    );
};

export function Sidebar() {
    const [isOpen, setIsOpen] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser, setRole } = useUser();

    if (!isOpen) return null;

    const isPathActive = (path: string) => location.pathname === path;

    // Role-based menu items
    const getMenuItems = () => {
        const commonItems = [
            {
                label: 'Dashboard',
                icon: Home,
                path: '/',
                onClick: () => navigate('/')
            }
        ];

        // MANAGEMENT (Top Level) - Views all opportunities, makes final decisions
        if (currentUser.role === 'MANAGEMENT') {
            return [
                ...commonItems,
                {
                    label: 'Management Dashboard',
                    icon: Award,
                    path: '/management',
                    onClick: () => navigate('/management'),
                    description: 'View submitted assessments and make final decisions'
                },
                {
                    label: 'Analytics',
                    icon: BarChart3,
                    path: '/analytics',
                    hasSubmenu: true
                }
            ];
        }

        // PRACTICE HEAD - Assigns SAs AND Reviews Assessments (2 tabs in one page)
        if (currentUser.role === 'PRACTICE_HEAD') {
            return [
                ...commonItems,
                {
                    label: 'Governance Dashboard',
                    icon: Award,
                    path: '/practice-head-review',
                    onClick: () => navigate('/practice-head-review'),
                    description: 'Assign opportunities to SAs & Review submitted assessments'
                },
                {
                    label: 'Analytics',
                    icon: BarChart3,
                    path: '/analytics',
                    hasSubmenu: true
                }
            ];
        }

        // SOLUTION ARCHITECT - Scores assigned opportunities
        if (currentUser.role === 'SOLUTION_ARCHITECT') {
            return [
                ...commonItems,
                {
                    label: 'Assigned to Me',
                    icon: UserCheck,
                    path: '/assigned-to-me',
                    onClick: () => navigate('/assigned-to-me'),
                    description: 'My assigned opportunities to score'
                }
            ];
        }

        return commonItems;
    };

    const menuItems = getMenuItems();

    return (
        <div className="w-80 h-screen bg-white border-r border-gray-200 flex flex-col shadow-sm flex-shrink-0 overflow-y-auto">
            {/* Header */}
            <div className="px-4 py-4 flex items-center justify-between sticky top-0 bg-white z-10 border-b border-gray-100">
                <button className="text-orange-500 hover:bg-orange-50 p-1 rounded">
                    <ArrowLeft size={20} />
                </button>
                <div className="text-xs font-medium text-gray-600">
                    {currentUser.role === 'MANAGEMENT' && 'Management View'}
                    {currentUser.role === 'PRACTICE_HEAD' && 'Practice Head View'}
                    {currentUser.role === 'SOLUTION_ARCHITECT' && 'SA View'}
                </div>
            </div>

            {/* User Info */}
            <div className="px-4 py-3 bg-blue-50 border-b border-blue-100">
                <div className="text-sm font-semibold text-blue-900">{currentUser.name}</div>
                <div className="text-xs text-blue-600">{currentUser.email}</div>
                <div className="text-xs text-blue-500 mt-1 capitalize">
                    Role: {currentUser.role.replace('_', ' ')}
                </div>
            </div>

            {/* Menu Items */}
            <div className="flex-1 py-2">
                <div className="px-4 py-2">
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        Navigation
                    </span>
                </div>
                {menuItems.map((item, index) => (
                    <SidebarItem
                        key={index}
                        label={item.label}
                        icon={item.icon}
                        hasSubmenu={item.hasSubmenu}
                        isActive={item.path ? isPathActive(item.path) : false}
                        onClick={item.onClick}
                        path={item.path}
                    />
                ))}
            </div>

            {/* Footer - Role Switcher (for demo) */}
            <div className="border-t border-gray-200 p-4 bg-gray-50">
                <div className="text-xs text-gray-500 mb-2 font-medium">Demo Role Switcher</div>
                <div className="flex gap-2">
                    <button
                        onClick={() => {
                            setRole('MANAGEMENT');
                            navigate('/');
                        }}
                        className={`flex-1 text-xs px-2 py-1.5 border rounded transition-colors ${currentUser.role === 'MANAGEMENT' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                        title="Management View"
                    >
                        Mgmt
                    </button>
                    <button
                        onClick={() => {
                            setRole('PRACTICE_HEAD');
                            navigate('/');
                        }}
                        className={`flex-1 text-xs px-2 py-1.5 border rounded transition-colors ${currentUser.role === 'PRACTICE_HEAD' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                        title="Practice Head View"
                    >
                        Practice
                    </button>
                    <button
                        onClick={() => {
                            setRole('SOLUTION_ARCHITECT');
                            navigate('/');
                        }}
                        className={`flex-1 text-xs px-2 py-1.5 border rounded transition-colors ${currentUser.role === 'SOLUTION_ARCHITECT' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                        title="Solution Architect View"
                    >
                        SA
                    </button>
                </div>
            </div>
        </div>
    );
}
