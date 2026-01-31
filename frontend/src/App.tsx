
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
import { ManagementDashboard } from './pages/ManagementDashboard';
import { PracticeHeadDashboard } from './pages/PracticeHeadDashboard';
import { SolutionArchitectDashboard } from './pages/SolutionArchitectDashboard';
import { OpportunityDetail } from './pages/OpportunityDetail';
import { Layout } from './components/Layout';

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<PracticeHeadDashboard />} />
                    <Route path="/opportunity-inbox" element={<OpportunityInbox />} />
                    <Route path="/opportunity/:id" element={<OpportunityDetail />} />
                    <Route path="/score/:id" element={<ScoreOpportunity />} />
                    <Route path="/management/dashboard" element={<ManagementDashboard />} />

                    {/* Practice Head Routes */}
                    <Route path="/practice-head/action-required" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/unassigned" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/assign" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/review" element={<PracticeHeadDashboard />} />
                    <Route path="/practice-head/metrics" element={<PracticeHeadDashboard />} />

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

