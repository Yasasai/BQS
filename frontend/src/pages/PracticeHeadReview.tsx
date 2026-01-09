import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Award, TrendingUp, CheckCircle, AlertCircle, Eye, FileText, Calendar, User, Send, UserPlus } from 'lucide-react';
import { Opportunity } from '../types';

interface SubmittedAssessment {
    id: number;
    opp_id: number;
    opportunity_name: string;
    customer: string;
    practice: string;
    deal_value: number;
    currency: string;
    assessed_by: string;
    submitted_at: string;
    score: number;
    recommendation: 'Pursue' | 'Caution' | 'No-Bid';
    confidence_level: 'High' | 'Medium' | 'Low';
}

type TabType = 'unassigned' | 'assigned';

export const PracticeHeadReview = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<TabType>('unassigned');

    // Unassigned opportunities state
    const [unassignedOpportunities, setUnassignedOpportunities] = useState<Opportunity[]>([]);
    const [selectedForAssignment, setSelectedForAssignment] = useState<number[]>([]);
    const [filterGeo, setFilterGeo] = useState('all');
    const [filterPractice, setFilterPractice] = useState('all');
    const [filterDealSize, setFilterDealSize] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    // Assigned/submitted assessments state
    const [assessments, setAssessments] = useState<SubmittedAssessment[]>([]);
    const [selectedAssessments, setSelectedAssessments] = useState<number[]>([]);
    const [filterRecommendation, setFilterRecommendation] = useState<string>('all');
    const [filterConfidence, setFilterConfidence] = useState<string>('all');

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (activeTab === 'unassigned') {
            fetchUnassignedOpportunities();
        } else {
            fetchSubmittedAssessments();
        }
    }, [activeTab]);

    const fetchUnassignedOpportunities = async () => {
        try {
            // TODO: API call
            const mockData: Opportunity[] = [
                {
                    id: 201,
                    remote_id: 'OPP-201',
                    name: 'Cloud Migration - ACME Corp',
                    customer: 'ACME Corporation',
                    practice: 'Cloud',
                    geo: 'North America',
                    deal_value: 2500000,
                    currency: 'USD',
                    win_probability: 75,
                    sales_owner: 'John Smith',
                    stage: 'Qualification',
                    close_date: '2026-06-30',
                    last_synced_at: '2026-01-08T10:00:00'
                },
                {
                    id: 202,
                    remote_id: 'OPP-202',
                    name: 'Cybersecurity Assessment - TechStart',
                    customer: 'TechStart Inc',
                    practice: 'Cybersecurity',
                    geo: 'Europe',
                    deal_value: 750000,
                    currency: 'USD',
                    win_probability: 60,
                    sales_owner: 'Jane Doe',
                    stage: 'Proposal',
                    close_date: '2026-05-15',
                    last_synced_at: '2026-01-07T14:30:00'
                }
            ];
            setUnassignedOpportunities(mockData);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching unassigned opportunities:', error);
            setLoading(false);
        }
    };

    const fetchSubmittedAssessments = async () => {
        try {
            // TODO: API call
            const mockData: SubmittedAssessment[] = [
                {
                    id: 1,
                    opp_id: 101,
                    opportunity_name: 'Cloud Migration - ACME Corp',
                    customer: 'ACME Corporation',
                    practice: 'Cloud',
                    deal_value: 2500000,
                    currency: 'USD',
                    assessed_by: 'Rajesh Kumar',
                    submitted_at: '2026-01-08T14:30:00',
                    score: 85,
                    recommendation: 'Pursue',
                    confidence_level: 'High'
                },
                {
                    id: 2,
                    opp_id: 102,
                    opportunity_name: 'Cybersecurity Assessment - TechStart',
                    customer: 'TechStart Inc',
                    practice: 'Cybersecurity',
                    deal_value: 750000,
                    currency: 'USD',
                    assessed_by: 'Priya Sharma',
                    submitted_at: '2026-01-07T11:15:00',
                    score: 62,
                    recommendation: 'Caution',
                    confidence_level: 'Medium'
                },
                {
                    id: 3,
                    opp_id: 103,
                    opportunity_name: 'ERP Implementation - GlobalTech',
                    customer: 'GlobalTech Solutions',
                    practice: 'ERP',
                    deal_value: 4200000,
                    currency: 'USD',
                    assessed_by: 'Amit Patel',
                    submitted_at: '2026-01-06T16:45:00',
                    score: 92,
                    recommendation: 'Pursue',
                    confidence_level: 'High'
                },
                {
                    id: 4,
                    opp_id: 104,
                    opportunity_name: 'Data Analytics Platform - RetailCo',
                    customer: 'RetailCo',
                    practice: 'Data & Analytics',
                    deal_value: 1800000,
                    currency: 'USD',
                    assessed_by: 'Sneha Reddy',
                    submitted_at: '2026-01-05T09:20:00',
                    score: 45,
                    recommendation: 'No-Bid',
                    confidence_level: 'High'
                }
            ];
            setAssessments(mockData);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching assessments:', error);
            setLoading(false);
        }
    };

    const handleAssignOpportunities = () => {
        if (selectedForAssignment.length === 0) {
            alert('Please select at least one opportunity to assign');
            return;
        }
        // TODO: Open assign modal
        alert(`Assigning ${selectedForAssignment.length} opportunity(ies) to Solution Architect`);
    };

    const handleSendToManagement = () => {
        if (selectedAssessments.length === 0) {
            alert('Please select at least one assessment to send to Management');
            return;
        }
        // TODO: API call
        alert(`Sending ${selectedAssessments.length} assessment(s) to Management for final approval`);
        setSelectedAssessments([]);
    };

    const getFilteredOpportunities = () => {
        return unassignedOpportunities.filter(opp => {
            const matchesGeo = filterGeo === 'all' || opp.geo === filterGeo;
            const matchesPractice = filterPractice === 'all' || opp.practice === filterPractice;
            const matchesSearch = searchQuery === '' ||
                opp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                opp.customer.toLowerCase().includes(searchQuery.toLowerCase());

            return matchesGeo && matchesPractice && matchesSearch;
        });
    };

    const getFilteredAssessments = () => {
        return assessments.filter(assessment => {
            const matchesRecommendation = filterRecommendation === 'all' || assessment.recommendation === filterRecommendation;
            const matchesConfidence = filterConfidence === 'all' || assessment.confidence_level === filterConfidence;
            const matchesSearch = searchQuery === '' ||
                assessment.opportunity_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                assessment.customer.toLowerCase().includes(searchQuery.toLowerCase());

            return matchesRecommendation && matchesConfidence && matchesSearch;
        });
    };

    const formatCurrency = (value: number, currency: string) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return `${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}, ${date.getFullYear()}`;
    };

    const getRecommendationColor = (recommendation: string) => {
        switch (recommendation) {
            case 'Pursue': return 'bg-green-100 text-green-800 border-green-200';
            case 'Caution': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'No-Bid': return 'bg-red-100 text-red-800 border-red-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getConfidenceColor = (confidence: string) => {
        switch (confidence) {
            case 'High': return 'text-green-600';
            case 'Medium': return 'text-yellow-600';
            case 'Low': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600 font-bold';
        if (score >= 60) return 'text-yellow-600 font-semibold';
        return 'text-red-600 font-semibold';
    };

    const filteredOpportunities = getFilteredOpportunities();
    const filteredAssessments = getFilteredAssessments();

    return (
        <div className="flex-1 flex flex-col h-full bg-gray-50">
            <TopBar title="Practice Head - Opportunity Management" />

            <div className="flex-1 overflow-auto p-6">
                {/* Header with Action Button */}
                <div className="mb-6 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                            <Award className="text-orange-500" size={28} />
                            {activeTab === 'unassigned' ? 'Assign Opportunities to SAs' : 'Review Submitted Assessments'}
                        </h1>
                        <p className="text-sm text-gray-600 mt-1">
                            {activeTab === 'unassigned'
                                ? 'Select opportunities and assign them to Solution Architects'
                                : 'Review SA assessments and send approved ones to Management'}
                        </p>
                    </div>
                    {activeTab === 'unassigned' && selectedForAssignment.length > 0 && (
                        <button
                            onClick={handleAssignOpportunities}
                            className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium"
                        >
                            <UserPlus size={18} />
                            Assign {selectedForAssignment.length} to SA
                        </button>
                    )}
                    {activeTab === 'assigned' && selectedAssessments.length > 0 && (
                        <button
                            onClick={handleSendToManagement}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                            <Send size={18} />
                            Send {selectedAssessments.length} to Management
                        </button>
                    )}
                </div>

                {/* Tabs */}
                <div className="mb-6 border-b border-gray-200">
                    <div className="flex gap-8">
                        <button
                            onClick={() => setActiveTab('unassigned')}
                            className={`pb-3 px-1 font-medium text-sm transition-colors relative ${activeTab === 'unassigned'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Unassigned ({unassignedOpportunities.length})
                        </button>
                        <button
                            onClick={() => setActiveTab('assigned')}
                            className={`pb-3 px-1 font-medium text-sm transition-colors relative ${activeTab === 'assigned'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            Assigned ({assessments.length})
                        </button>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder={activeTab === 'unassigned' ? "Search by opportunity or customer..." : "Search by opportunity, customer, or SA..."}
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        {activeTab === 'unassigned' ? (
                            <>
                                <select
                                    value={filterGeo}
                                    onChange={(e) => setFilterGeo(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">All Geographies</option>
                                    <option value="North America">North America</option>
                                    <option value="Europe">Europe</option>
                                    <option value="Asia Pacific">Asia Pacific</option>
                                </select>

                                <select
                                    value={filterPractice}
                                    onChange={(e) => setFilterPractice(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">All Practices</option>
                                    <option value="Cloud">Cloud</option>
                                    <option value="Cybersecurity">Cybersecurity</option>
                                    <option value="ERP">ERP</option>
                                    <option value="Data & Analytics">Data & Analytics</option>
                                </select>

                                <select
                                    value={filterDealSize}
                                    onChange={(e) => setFilterDealSize(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">Any Deal Size</option>
                                    <option value="small">{'< $500K'}</option>
                                    <option value="medium">$500K - $2M</option>
                                    <option value="large">{'> $2M'}</option>
                                </select>
                            </>
                        ) : (
                            <>
                                <select
                                    value={filterRecommendation}
                                    onChange={(e) => setFilterRecommendation(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">All Recommendations</option>
                                    <option value="Pursue">Pursue</option>
                                    <option value="Caution">Caution</option>
                                    <option value="No-Bid">No-Bid</option>
                                </select>

                                <select
                                    value={filterConfidence}
                                    onChange={(e) => setFilterConfidence(e.target.value)}
                                    className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">All Confidence Levels</option>
                                    <option value="High">High Confidence</option>
                                    <option value="Medium">Medium Confidence</option>
                                    <option value="Low">Low Confidence</option>
                                </select>
                            </>
                        )}
                    </div>
                </div>

                {/* Content based on active tab */}
                {activeTab === 'unassigned' ? (
                    /* Unassigned Opportunities Table */
                    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-4 py-3 text-left">
                                        <input
                                            type="checkbox"
                                            checked={selectedForAssignment.length === filteredOpportunities.length && filteredOpportunities.length > 0}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedForAssignment(filteredOpportunities.map(o => o.id));
                                                } else {
                                                    setSelectedForAssignment([]);
                                                }
                                            }}
                                            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                        />
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Opportunity
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Practice
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Deal Value
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Geo
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Stage
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Close Date
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {loading ? (
                                    <tr>
                                        <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                                            Loading opportunities...
                                        </td>
                                    </tr>
                                ) : filteredOpportunities.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                                            No unassigned opportunities found
                                        </td>
                                    </tr>
                                ) : (
                                    filteredOpportunities.map((opp) => (
                                        <tr key={opp.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-4 py-4">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedForAssignment.includes(opp.id)}
                                                    onChange={() => {
                                                        setSelectedForAssignment(prev =>
                                                            prev.includes(opp.id) ? prev.filter(id => id !== opp.id) : [...prev, opp.id]
                                                        );
                                                    }}
                                                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                                />
                                            </td>
                                            <td className="px-4 py-4">
                                                <div>
                                                    <div className="text-sm font-medium text-gray-900">{opp.name}</div>
                                                    <div className="text-xs text-gray-500">{opp.customer}</div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm text-gray-700">{opp.practice}</span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm font-semibold text-gray-900">
                                                    {formatCurrency(opp.deal_value, opp.currency)}
                                                </span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm text-gray-700">{opp.geo}</span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm text-gray-700">{opp.stage}</span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm text-gray-600">{formatDate(opp.close_date)}</span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    /* Submitted Assessments Table */
                    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-4 py-3 text-left">
                                        <input
                                            type="checkbox"
                                            checked={selectedAssessments.length === filteredAssessments.length && filteredAssessments.length > 0}
                                            onChange={(e) => {
                                                if (e.target.checked) {
                                                    setSelectedAssessments(filteredAssessments.map(a => a.id));
                                                } else {
                                                    setSelectedAssessments([]);
                                                }
                                            }}
                                            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                        />
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Opportunity
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Practice
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Deal Value
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Score
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Recommendation
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Confidence
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Assessed By
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Submitted
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Action
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {loading ? (
                                    <tr>
                                        <td colSpan={10} className="px-4 py-8 text-center text-gray-500">
                                            Loading assessments...
                                        </td>
                                    </tr>
                                ) : filteredAssessments.length === 0 ? (
                                    <tr>
                                        <td colSpan={10} className="px-4 py-8 text-center text-gray-500">
                                            No submitted assessments found
                                        </td>
                                    </tr>
                                ) : (
                                    filteredAssessments.map((assessment) => (
                                        <tr key={assessment.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-4 py-4">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedAssessments.includes(assessment.id)}
                                                    onChange={() => {
                                                        setSelectedAssessments(prev =>
                                                            prev.includes(assessment.id) ? prev.filter(id => id !== assessment.id) : [...prev, assessment.id]
                                                        );
                                                    }}
                                                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                                />
                                            </td>
                                            <td className="px-4 py-4">
                                                <div>
                                                    <div className="text-sm font-medium text-gray-900">
                                                        {assessment.opportunity_name}
                                                    </div>
                                                    <div className="text-xs text-gray-500">
                                                        {assessment.customer}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm text-gray-700">{assessment.practice}</span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className="text-sm font-semibold text-gray-900">
                                                    {formatCurrency(assessment.deal_value, assessment.currency)}
                                                </span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className={`text-xl font-bold ${getScoreColor(assessment.score)}`}>
                                                    {assessment.score}
                                                </span>
                                                <span className="text-xs text-gray-500">/100</span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRecommendationColor(assessment.recommendation)}`}>
                                                    {assessment.recommendation}
                                                </span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <span className={`text-sm font-medium ${getConfidenceColor(assessment.confidence_level)}`}>
                                                    {assessment.confidence_level}
                                                </span>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="flex items-center gap-2">
                                                    <User size={14} className="text-gray-400" />
                                                    <span className="text-sm text-gray-700">{assessment.assessed_by}</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <div className="flex items-center gap-2">
                                                    <Calendar size={14} className="text-gray-400" />
                                                    <span className="text-sm text-gray-600">
                                                        {formatDate(assessment.submitted_at)}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4">
                                                <button
                                                    onClick={() => navigate(`/opportunity/${assessment.opp_id}`)}
                                                    className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
                                                >
                                                    <Eye size={14} />
                                                    Review
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};
