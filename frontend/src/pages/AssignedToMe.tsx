import React, { useEffect, useState } from 'react';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

type AssessmentStatus = 'not-started' | 'draft' | 'submitted';

interface AssessmentData extends Opportunity {
    assessment_status?: AssessmentStatus;
    score?: number;
    score_status?: string;
    scored_by?: string;
}

export function AssignedToMe() {
    const navigate = useNavigate();
    const [opportunities, setOpportunities] = useState<AssessmentData[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<AssessmentStatus | 'all'>('not-started');

    // Filter states
    const [selectedPractice, setSelectedPractice] = useState('All Practices');
    const [selectedGeo, setSelectedGeo] = useState('All Geos');
    const [selectedValue, setSelectedValue] = useState('All Values');

    useEffect(() => {
        fetchAssignedOpportunities();
    }, []);

    const fetchAssignedOpportunities = () => {
        setLoading(true);
        fetch('http://localhost:8000/api/opportunities')
            .then(res => res.json())
            .then(data => {
                // Filter only assigned opportunities (those with sales_owner)
                const assigned = data.filter((opp: Opportunity) =>
                    opp.sales_owner && opp.sales_owner !== 'N/A'
                );

                // Mock assessment status for demo - in real app, fetch from assessments table
                const withAssessments = assigned.map((opp: Opportunity) => ({
                    ...opp,
                    assessment_status: Math.random() > 0.5 ? 'submitted' :
                        Math.random() > 0.5 ? 'draft' : 'not-started',
                    score: Math.random() > 0.3 ? Math.floor(Math.random() * 40) + 60 : undefined,
                    score_status: Math.random() > 0.5 ? 'Submitted' :
                        Math.random() > 0.5 ? 'Draft' : 'Not Started',
                    scored_by: opp.sales_owner
                }));

                setOpportunities(withAssessments);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunities", err);
                setLoading(false);
            });
    };

    // Filter opportunities based on active tab and filters
    const getFilteredOpportunities = () => {
        let filtered = opportunities;

        // Tab filtering
        if (activeTab !== 'all') {
            filtered = filtered.filter(o => o.assessment_status === activeTab);
        }

        // Practice filtering
        if (selectedPractice !== 'All Practices') {
            filtered = filtered.filter(o => o.practice === selectedPractice);
        }

        // Geo filtering
        if (selectedGeo !== 'All Geos') {
            filtered = filtered.filter(o => o.geo === selectedGeo);
        }

        return filtered;
    };

    const filteredOpportunities = getFilteredOpportunities();

    // Calculate tab counts
    const notStartedCount = opportunities.filter(o => o.assessment_status === 'not-started').length;
    const draftCount = opportunities.filter(o => o.assessment_status === 'draft').length;
    const submittedCount = opportunities.filter(o => o.assessment_status === 'submitted').length;

    const handleRowClick = (oppId: number) => {
        // Navigate to opportunity detail page
        navigate(`/opportunity/${oppId}`);
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Back Navigation */}
                <div className="px-6 pt-4">
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                        <ChevronLeft size={16} />
                        Back to Opportunity Inbox
                    </button>
                </div>

                {/* Page Title */}
                <div className="px-6 pt-4 pb-4">
                    <h1 className="text-2xl font-semibold text-gray-900">Solution Architect 'Assigned to Me' Inbox</h1>
                </div>

                {/* Tabs and Filters Row */}
                <div className="px-6 pb-4">
                    <div className="flex items-center justify-between gap-4">
                        {/* Status Tabs */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => setActiveTab('all')}
                                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${activeTab === 'all'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                All
                            </button>
                            <button
                                onClick={() => setActiveTab('not-started')}
                                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${activeTab === 'not-started'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                Not Started
                            </button>
                            <button
                                onClick={() => setActiveTab('draft')}
                                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${activeTab === 'draft'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                Draft
                            </button>
                            <button
                                onClick={() => setActiveTab('submitted')}
                                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${activeTab === 'submitted'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                Submitted
                            </button>
                        </div>

                        {/* Filter Dropdowns */}
                        <div className="flex gap-3">
                            <select
                                value={selectedPractice}
                                onChange={(e) => setSelectedPractice(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>All Practices</option>
                                <option>Infrastructure</option>
                                <option>Healthcare</option>
                                <option>Financial Services</option>
                                <option>Education</option>
                                <option>Automotive</option>
                                <option>Logistics</option>
                                <option>Utilities</option>
                            </select>
                            <select
                                value={selectedGeo}
                                onChange={(e) => setSelectedGeo(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>All Geos</option>
                                <option>North America</option>
                                <option>Europe</option>
                                <option>Asia Pacific</option>
                                <option>Latin America</option>
                            </select>
                            <select
                                value={selectedValue}
                                onChange={(e) => setSelectedValue(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded text-sm bg-white hover:border-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option>All Values</option>
                                <option>&lt; $1M</option>
                                <option>$1M - $3M</option>
                                <option>&gt; $3M</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Results Count */}
                <div className="px-6 py-3 bg-white border-y border-gray-200">
                    <span className="text-sm text-gray-600">
                        Showing <span className="font-semibold text-gray-900">{filteredOpportunities.length}</span> of {opportunities.length} opportunities
                    </span>
                </div>

                {/* Table Section */}
                <div className="flex-1 overflow-auto bg-white">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Opp ID</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Customer</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Name</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Practice</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Value</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Win %</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Assessment Score</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Score Status</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Last Scored By</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr><td colSpan={10} className="px-6 py-12 text-center text-gray-500">Loading opportunities...</td></tr>
                            ) : filteredOpportunities.length === 0 ? (
                                <tr><td colSpan={10} className="px-6 py-12 text-center text-gray-500">No opportunities found.</td></tr>
                            ) : (
                                filteredOpportunities.map((opp) => (
                                    <tr
                                        key={opp.id}
                                        className="hover:bg-blue-50 transition-colors"
                                    >
                                        <td
                                            className="px-6 py-4 whitespace-nowrap cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            <div className="text-sm font-medium text-blue-600 hover:underline">
                                                {opp.remote_id || `OPP-${opp.id}`}
                                            </div>
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            <div className="text-sm text-gray-900">{opp.customer}</div>
                                        </td>
                                        <td
                                            className="px-6 py-4 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            <div className="text-sm text-gray-900 max-w-xs truncate">{opp.name}</div>
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {opp.practice || '-'}
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', maximumFractionDigits: 2 }).format(opp.deal_value)}
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {opp.win_probability ? `${opp.win_probability}%` : '-'}
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {opp.score ? `${opp.score}%` : '-'}
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {opp.score_status === 'Submitted' ? (
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                    Submitted
                                                </span>
                                            ) : opp.score_status === 'Draft' ? (
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                    Draft
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                                    Not Started
                                                </span>
                                            )}
                                        </td>
                                        <td
                                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 cursor-pointer"
                                            onClick={() => handleRowClick(opp.id)}
                                        >
                                            {opp.scored_by || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {opp.assessment_status === 'draft' || opp.assessment_status === 'not-started' ? (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        navigate(`/score/${opp.id}`);
                                                    }}
                                                    className="px-4 py-2 bg-orange-600 text-white text-xs font-medium rounded hover:bg-orange-700 transition-colors"
                                                >
                                                    Score Now
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        // TODO: API call to submit to Practice Head
                                                        alert(`Submitting assessment for ${opp.name} to Practice Head for review`);
                                                    }}
                                                    className="px-4 py-2 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
                                                >
                                                    Submit to Practice Head
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="px-6 py-4 bg-white border-t border-gray-200 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                        Showing 1 of {Math.ceil(filteredOpportunities.length / 10)} pages
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50" disabled>
                            ← Previous
                        </button>
                        <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded">1</button>
                        <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900">2</button>
                        <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900">...</button>
                        <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900">
                            Next →
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
