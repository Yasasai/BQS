import React from 'react';
import { X, LayoutDashboard, Inbox, FileText, Users, Settings, TrendingUp, CheckSquare, UserCheck, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

export const RoleSidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    const { user } = useAuth();
    const navigate = useNavigate();

    if (!isOpen) return null;

    // Determine user role
    const isPracticeHead = user?.role === 'PH';
    const isSolutionArchitect = user?.role === 'SA' || user?.role === 'SP';
    const isManagement = user?.role === 'GH' || user?.role === 'SH';

    const handleNavigation = (path: string) => {
        navigate(path);
        onClose();
    };

    return (
        <>
            {/* Overlay */}
            <div
                className="sidebar-overlay"
                onClick={onClose}
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    zIndex: 999
                }}
            />

            {/* Sidebar */}
            <div
                className="sidebar"
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '280px',
                    height: '100vh',
                    backgroundColor: 'white',
                    boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
                    zIndex: 1000,
                    display: 'flex',
                    flexDirection: 'column',
                    animation: 'slideIn 0.3s ease-out'
                }}
            >
                {/* Header */}
                <div style={{
                    padding: '16px',
                    borderBottom: '1px solid #E0E0E0',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    backgroundColor: '#F5F1E3'
                }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>
                        BQS Menu
                    </h2>
                    <button
                        onClick={onClose}
                        className="oracle-icon-btn"
                        aria-label="Close menu"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* User Info */}
                <div style={{
                    padding: '16px',
                    borderBottom: '1px solid #E0E0E0',
                    backgroundColor: '#FAFAFA'
                }}>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: '#212121' }}>
                        {user?.name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#757575', marginTop: '4px' }}>
                        {user?.email}
                    </div>
                    <div style={{ fontSize: '11px', color: '#1976D2', marginTop: '8px' }}>
                        {user?.role?.replace('_', ' ')}
                    </div>
                </div>

                {/* Menu Items */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>

                    {isManagement && (
                        <>
                            <div style={{
                                padding: '8px 16px',
                                fontSize: '11px',
                                fontWeight: 600,
                                color: '#757575',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px'
                            }}>
                                Management
                            </div>

                            <MenuItem
                                icon={<TrendingUp size={18} />}
                                label="Management Dashboard"
                                onClick={() => handleNavigation('/management/dashboard')}
                            />
                        </>
                    )}

                    {isPracticeHead && (
                        <>
                            <div style={{
                                padding: '8px 16px',
                                fontSize: '11px',
                                fontWeight: 600,
                                color: '#757575',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                marginTop: isManagement ? '16px' : '0'
                            }}>
                                Practice Head
                            </div>

                            <MenuItem
                                icon={<Inbox size={18} />}
                                label="Assign Pipeline"
                                onClick={() => handleNavigation('/practice-head/unassigned')}
                            />

                            <MenuItem
                                icon={<UserCheck size={18} />}
                                label="Work Pipeline"
                                onClick={() => handleNavigation('/practice-head/assigned')}
                            />

                            <MenuItem
                                icon={<FileText size={18} />}
                                label="Review Pipeline"
                                onClick={() => handleNavigation('/practice-head/review')}
                            />

                            <MenuItem
                                icon={<CheckSquare size={18} />}
                                label="Completed Assessments"
                                onClick={() => handleNavigation('/practice-head/completed')}
                            />

                            <MenuItem
                                icon={<LayoutDashboard size={18} />}
                                label="All Opportunities"
                                onClick={() => handleNavigation('/')}
                            />

                        </>
                    )}

                    {isSolutionArchitect && (
                        <>
                            <div style={{
                                padding: '8px 16px',
                                fontSize: '11px',
                                fontWeight: 600,
                                color: '#757575',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                marginTop: (isPracticeHead || isManagement) ? '16px' : '0'
                            }}>
                                Solution Architect
                            </div>

                            <MenuItem
                                icon={<Inbox size={18} />}
                                label="My Assigned Opportunities"
                                onClick={() => handleNavigation('/sa/assigned')}
                            />

                            <MenuItem
                                icon={<FileText size={18} />}
                                label="Start Assessment"
                                onClick={() => handleNavigation('/sa/start')}
                            />

                            <MenuItem
                                icon={<CheckSquare size={18} />}
                                label="Submitted Assessments"
                                onClick={() => handleNavigation('/sa/submitted')}
                            />
                        </>
                    )}

                    {/* COMMON SECTION */}
                    <div style={{
                        padding: '8px 16px',
                        fontSize: '11px',
                        fontWeight: 600,
                        color: '#757575',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        marginTop: '16px',
                        borderTop: '1px solid #E0E0E0',
                        paddingTop: '16px'
                    }}>
                        General
                    </div>

                    <MenuItem
                        icon={<Settings size={18} />}
                        label="Settings"
                        onClick={() => handleNavigation('/settings')}
                    />
                </div>

                {/* Footer */}
                <div style={{
                    padding: '16px',
                    borderTop: '1px solid #E0E0E0',
                    fontSize: '11px',
                    color: '#757575',
                    textAlign: 'center'
                }}>
                    BQS v1.0 - Bid Qualification System
                </div>
            </div>

            <style>{`
                @keyframes slideIn {
                    from {
                        transform: translateX(-100%);
                    }
                    to {
                        transform: translateX(0);
                    }
                }
            `}</style>
        </>
    );
};

// Menu Item Component
interface MenuItemProps {
    icon: React.ReactNode;
    label: string;
    onClick: () => void;
}

const MenuItem: React.FC<MenuItemProps> = ({ icon, label, onClick }) => {
    return (
        <button
            onClick={onClick}
            style={{
                width: '100%',
                padding: '12px 16px',
                border: 'none',
                background: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: 'pointer',
                fontSize: '14px',
                color: '#212121',
                transition: 'background-color 0.2s',
                textAlign: 'left'
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#FFF9C4';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
            }}
        >
            <span style={{ color: '#757575', display: 'flex' }}>{icon}</span>
            <span>{label}</span>
        </button>
    );
};
