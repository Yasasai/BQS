
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
import { ManagementDashboard } from './pages/ManagementDashboard';
import { SalesHeadDashboard } from './pages/SalesHeadDashboard';
import { PracticeHeadDashboard } from './pages/PracticeHeadDashboard';
import { SolutionArchitectDashboard } from './pages/SolutionArchitectDashboard';
import { OpportunityDetail } from './pages/OpportunityDetail';
import { Layout } from './components/Layout';

import { useAuth } from './context/AuthContext';
import { Navigate } from 'react-router-dom';

const HomeRedirect = () => {
    const { user } = useAuth();
    if (user?.role === 'GH') return <Navigate to="/management/dashboard" replace />;
    if (user?.role === 'SH') return <Navigate to="/sales/dashboard" replace />;
    if (user?.role === 'PH') return <Navigate to="/practice-head/dashboard" replace />;
    if (user?.role === 'SA' || user?.role === 'SP') return <Navigate to="/assigned-to-me" replace />;
    return <PracticeHeadDashboard />;
};

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<HomeRedirect />} />
                    <Route path="/opportunity-inbox" element={<OpportunityInbox />} />
                    <Route path="/opportunity/:id" element={<OpportunityDetail />} />
                    <Route path="/score/:id" element={<ScoreOpportunity />} />
                    <Route path="/management/dashboard" element={<ManagementDashboard />} />

                    {/* Practice Head Routes */}
                    <Route path="/practice-head/dashboard" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/action-required" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/in-progress" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/review" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/completed" element={<PracticeHeadDashboard />} />

                    {/* Sales Head Routes */}
                    <Route path="/sales/*" element={<SalesHeadDashboard />} />
                    <Route path="/sales/action-required" element={<SalesHeadDashboard />} />
                    <Route path="/sales/in-progress" element={<SalesHeadDashboard />} />
                    <Route path="/sales/review" element={<SalesHeadDashboard />} />
                    <Route path="/sales/completed" element={<SalesHeadDashboard />} />

                    {/* SA Routes */}
                    <Route path="/assigned-to-me" element={<SolutionArchitectDashboard />} />
                    <Route path="/sa/assigned" element={<SolutionArchitectDashboard />} />
                    <Route path="/sa/start" element={<SolutionArchitectDashboard />} />
                    <Route path="/sa/submitted" element={<SolutionArchitectDashboard />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;

