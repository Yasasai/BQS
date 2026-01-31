import React, { useState } from 'react';
import { Search, Bell, Star, MessageSquare, User } from 'lucide-react';
import { RoleSidebar } from './RoleSidebar';

export const OracleHeader: React.FC = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <>
            <header className="oracle-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button
                        className="oracle-icon-btn"
                        aria-label="Menu"
                        onClick={() => setSidebarOpen(true)}
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>

                    <div className="oracle-logo" style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        <span>inspira</span>
                        <span className="oracle-logo-badge" style={{
                            display: 'inline-flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            textAlign: 'center',
                            lineHeight: '1.2',
                            marginTop: '-4px'
                        }}>
                            Great<br />Place<br />To<br />Work<br />Certified
                        </span>
                    </div>
                </div>

                <div className="oracle-header-actions">
                    <button className="oracle-icon-btn" aria-label="Search">
                        <Search size={20} />
                    </button>

                    <button className="oracle-icon-btn" aria-label="Notifications">
                        <Bell size={20} />
                        <span className="badge">1</span>
                    </button>

                    <button className="oracle-icon-btn" aria-label="Favorites">
                        <Star size={20} />
                    </button>

                    <button className="oracle-icon-btn" aria-label="Messages">
                        <MessageSquare size={20} />
                    </button>

                    <button className="oracle-icon-btn" aria-label="Profile">
                        <User size={20} />
                    </button>
                </div>
            </header>

            <RoleSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        </>
    );
};
