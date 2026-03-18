import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
import { UnifiedDashboard } from './pages/UnifiedDashboard';
import { OpportunityDetail } from './pages/OpportunityDetail';
import { Layout } from './components/Layout';
import { UserProvider } from './context/UserContext';
import { BidManagerWorkspace } from './pages/BidManagerWorkspace';
import AdminDashboard from './pages/AdminDashboard';

import { useAuth, UserRole } from './context/AuthContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: UserRole[] }) => {
    const { user, isAuthenticated } = useAuth();
    if (!isAuthenticated) return <Navigate to="/" replace />;
    if (allowedRoles && !allowedRoles.includes(user?.role as UserRole)) {
        // Redirect to their own dashboard if they hit the wrong route
        return <Navigate to="/" replace />;
    }
    return <>{children}</>;
};

// ─── Login Screen (shown when user is not authenticated) ─────────────────────
const LoginScreen = () => {
    const { login, devLogin, availableUsers, isLoadingUsers } = useAuth();
    const [loading, setLoading] = React.useState<string | null>(null);
    const [error, setError] = React.useState<string | null>(null);

    const handleLogin = async (email: string) => {
        setLoading(email);
        setError(null);
        try {
            await login(email);
        } catch (err: any) {
            setError(err?.message || 'Login failed. Ensure the backend is running.');
        } finally {
            setLoading(null);
        }
    };

    const handleDevLogin = async (role: string) => {
        setLoading(`dev-${role}`);
        setError(null);
        try {
            await devLogin(role);
        } catch (err: any) {
            setError(err?.message || 'Dev Login failed.');
        } finally {
            setLoading(null);
        }
    };

    const getRoleIcon = (roles: string[]) => {
        if (roles.includes('GH')) return '🌐';
        if (roles.includes('PSH')) return '🎯';
        if (roles.includes('PH')) return '🏛️';
        if (roles.includes('SH')) return '💼';
        if (roles.includes('SA')) return '🔧';
        return '🤝';
    };

    const getPrimaryRole = (roles: string[]) => {
        const roleLabels: Record<string, string> = {
            GH: 'Global Head',
            PSH: 'Presales Head',
            PH: 'Practice Head',
            SH: 'Sales Head',
            SA: 'Solution Architect',
            SP: 'Sales Person'
        };
        return roles.map(r => roleLabels[r] || r).join(', ');
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: "'Inter', sans-serif",
            padding: '24px',
        }}>
            <div style={{ width: '100%', maxWidth: 480 }}>
                <div style={{ textAlign: 'center', marginBottom: 40 }}>
                    <div style={{
                        display: 'inline-flex',
                        background: 'rgba(99, 102, 241, 0.1)',
                        padding: '8px 16px',
                        borderRadius: '99px',
                        color: '#818cf8',
                        fontSize: '12px',
                        fontWeight: 700,
                        letterSpacing: '0.1em',
                        marginBottom: '16px'
                    }}>
                        BQS PORTAL V2
                    </div>
                    <h1 style={{ color: '#fff', fontSize: '32px', fontWeight: 800, margin: '0 0 12px' }}>
                        Enterprise Bid Console
                    </h1>
                    <p style={{ color: '#94a3b8', fontSize: '15px' }}>
                        Unified Opportunity Lifecycle & Scoring
                    </p>
                </div>

                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.2)',
                        padding: '16px',
                        borderRadius: '12px',
                        marginBottom: '24px',
                        color: '#f87171',
                        fontSize: '14px'
                    }}>
                        {error}
                    </div>
                )}

                <div style={{ display: 'grid', gap: '12px', maxHeight: '400px', overflowY: 'auto', paddingRight: '8px' }}>
                    {isLoadingUsers ? (
                        <div style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>
                            <div style={{ width: '24px', height: '24px', border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.6s linear infinite', margin: '0 auto 10px' }} />
                            Loading users from database...
                        </div>
                    ) : availableUsers.length === 0 ? (
                        <div style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>
                            No users found in database.
                        </div>
                    ) : (
                        availableUsers.map((u) => (
                            <button
                                key={u.user_id}
                                onClick={() => handleLogin(u.email)}
                                disabled={!!loading}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '16px',
                                    background: 'rgba(255, 255, 255, 0.03)',
                                    border: '1px solid rgba(255, 255, 255, 0.08)',
                                    padding: '16px 20px',
                                    borderRadius: '16px',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    textAlign: 'left',
                                    width: '100%',
                                    opacity: loading && loading !== u.email ? 0.5 : 1
                                }}
                                onMouseEnter={e => {
                                    if (!loading) {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)';
                                        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
                                    }
                                }}
                                onMouseLeave={e => {
                                    if (!loading) {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                                    }
                                }}
                            >
                                <span style={{ fontSize: '24px' }}>{getRoleIcon(u.roles)}</span>
                                <div style={{ flex: 1 }}>
                                    <div style={{ color: '#fff', fontWeight: 600, fontSize: '15px' }}>{u.display_name}</div>
                                    <div style={{ color: '#64748b', fontSize: '11px' }}>{getPrimaryRole(u.roles)} • {u.email}</div>
                                </div>
                                {loading === u.email && (
                                    <div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }} />
                                )}
                            </button>
                        ))
                    )}
                </div>

                {/* Development Access Bypass */}
                <div style={{ marginTop: '32px', paddingTop: '32px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <h3 style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px', textAlign: 'center' }}>
                        Quick Role Login (Auto-selects First User)
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                        {['GH', 'PSH', 'PH', 'SH', 'SA', 'SP'].map((role) => (
                            <button
                                key={`dev-${role}`}
                                onClick={() => handleDevLogin(role)}
                                disabled={!!loading}
                                style={{
                                    background: 'rgba(255, 255, 255, 0.05)',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    color: '#fff',
                                    padding: '10px',
                                    borderRadius: '8px',
                                    fontSize: '11px',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    opacity: loading && loading !== `dev-${role}` ? 0.5 : 1
                                }}
                                onMouseEnter={e => {
                                    if (!loading) {
                                        e.currentTarget.style.background = 'rgba(99, 102, 241, 0.2)';
                                        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
                                    }
                                }}
                                onMouseLeave={e => {
                                    if (!loading) {
                                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                                    }
                                }}
                            >
                                {role}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                ::-webkit-scrollbar { width: 4px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
                ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
            `}</style>
        </div>
    );
};

// ─── Home redirect ───────────────────────────────────────────────────────────
const HomeRedirect = () => {
    const { isAuthenticated } = useAuth();
    if (!isAuthenticated) return <LoginScreen />;
    return <Navigate to="/dashboard" replace />;
};

function App() {
    return (
        <AuthProvider>
            <UserProvider>
                <Router>
                    <Layout>
                        <Routes>
                            <Route path="/" element={<HomeRedirect />} />

                            {/* Unified Dashboard for all roles */}
                            <Route path="/dashboard" element={
                                <ProtectedRoute>
                                    <UnifiedDashboard />
                                </ProtectedRoute>
                            } />

                            {/* Legacy Dashboard Route Aliases (all pointing to UnifiedDashboard) */}
                            <Route path="/management/*" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/sales/*" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/practice-head/*" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/assigned-to-me" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/sa/*" element={<Navigate to="/dashboard" replace />} />

                            {/* Functional Routes */}
                            <Route path="/opportunity-inbox" element={<ProtectedRoute><OpportunityInbox /></ProtectedRoute>} />
                            <Route path="/opportunity/:id" element={<ProtectedRoute><BidManagerWorkspace /></ProtectedRoute>} />
                            <Route path="/score/:id" element={<ProtectedRoute><BidManagerWorkspace /></ProtectedRoute>} />
                            <Route path="/admin" element={
                                <ProtectedRoute allowedRoles={['GH']}>
                                    <AdminDashboard />
                                </ProtectedRoute>
                            } />
                        </Routes>
                    </Layout>
                </Router>
            </UserProvider>
        </AuthProvider>
    );
}

export default App;
