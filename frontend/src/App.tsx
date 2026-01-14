
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { OpportunityInbox } from './pages/OpportunityInbox';
import { ScoreOpportunity } from './pages/ScoreOpportunity';
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
                    </Routes>
                </Layout>
            </Router>
        </UserProvider>
    );
}

export default App;
