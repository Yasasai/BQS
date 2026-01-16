
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
import { ManagementDashboard } from './pages/ManagementDashboard';
import { Layout } from './components/Layout';
import { UserProvider } from './context/UserContext';

function App() {
    return (
        <UserProvider>
            <Router>
                <Layout>
                    <Routes>
                        <Route path="/" element={<OpportunityInbox />} />
                        <Route path="/score/:id" element={<ScoreOpportunity />} />
                        <Route path="/management/dashboard" element={<ManagementDashboard />} />
                    </Routes>
                </Layout>
            </Router>
        </UserProvider>
    );
}

export default App;

