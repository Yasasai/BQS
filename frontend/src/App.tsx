import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { AssignedToMe } from './pages/AssignedToMe';
import { OpportunityDetail } from './pages/OpportunityDetail';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
import { PracticeHeadReview } from './pages/PracticeHeadReview';
import { ManagementDashboard } from './pages/ManagementDashboard';
import { Layout } from './components/Layout';
import { UserProvider } from './context/UserContext';

function App() {
    return (
        <UserProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Layout><OpportunityInbox /></Layout>} />
                    <Route path="/assigned-to-me" element={<Layout><AssignedToMe /></Layout>} />
                    <Route path="/opportunity/:id" element={<Layout><OpportunityDetail /></Layout>} />
                    <Route path="/score/:id" element={<Layout><ScoreOpportunity /></Layout>} />
                    <Route path="/practice-head-review" element={<Layout><PracticeHeadReview /></Layout>} />
                    <Route path="/management" element={<Layout><ManagementDashboard /></Layout>} />
                </Routes>
            </Router>
        </UserProvider>
    );
}

export default App;
