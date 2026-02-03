import React from 'react';
import './DashboardActions.css';

export const DashboardActions: React.FC = () => {
    
    const handleAccept = () => {
        alert('Action Accepted!');
    };

    const handleReject = () => {
        alert('Action Rejected!');
    };

    const handleViewChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const view = event.target.value;
        alert(`Switched to ${view} view`);
    };

    return (
        <div className="dashboard-actions">
            <div className="actions-card">
                <h3>Actions</h3>
                <button id="acceptBtn" className="btn accept" onClick={handleAccept}>Accept</button>
                <button id="rejectBtn" className="btn reject" onClick={handleReject}>Reject</button>
            </div>

            <div className="view-selector">
                <label htmlFor="dashboardView">Select Dashboard View</label>
                <select id="dashboardView" onChange={handleViewChange}>
                    <option value="daily">Daily View</option>
                    <option value="weekly">Weekly View</option>
                    <option value="monthly">Monthly View</option>
                </select>
            </div>
        </div>
    );
};
