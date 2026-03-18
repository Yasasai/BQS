import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { useAuth } from '../context/AuthContext';
import { Award, TrendingUp, CheckCircle, AlertCircle, Eye, FileText, Calendar, User } from 'lucide-react';

interface SubmittedAssessment {
    id: string;
    opp_id: string;
    opportunity_name: string;
    customer: string;
    practice: string;
    deal_value: number;
    currency: string;
    assessed_by: string;
    submitted_at: string;
    weighted_score: number;
    recommendation: 'Pursue' | 'Caution' | 'No-Bid' | string;
    confidence_level: 'High' | 'Medium' | 'Low' | string;
}

export const LeadershipDashboard = () => {
    const navigate = useNavigate();
    const { authFetch } = useAuth();
    const [assessments, setAssessments] = useState<SubmittedAssessment[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterRecommendation, setFilterRecommendation] = useState<string>('all');
    const [filterConfidence, setFilterConfidence] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchSubmittedAssessments();
    }, []);

    const fetchSubmittedAssessments = async () => {
        try {
            setLoading(true);
            // Fetch opportunities with 'review' tab to get submitted assessments
            const response = await authFetch('/api/opportunities/?tab=submitted&limit=100');

            if (!response.ok) throw new Error("Failed to fetch");

            const data = await response.json();

            const mappedData: SubmittedAssessment[] = data.items.map((item: any) => ({
                id: item.id,
                opp_id: item.id,
                opportunity_name: item.name,
                customer: item.customer,
                practice: item.practice,
                deal_value: item.deal_value,
                currency: item.currency,
                assessed_by: item.assigned_sa || item.assigned_sp || 'Unknown',
                submitted_at: item.close_date || new Date().toISOString(),
                weighted_score: item.win_probability || 0,
                recommendation: item.recommendation || 'Caution',
                confidence_level: item.confidence_level || 'Medium'
            }));

            setAssessments(mappedData);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching assessments:', error);
            setLoading(false);
        }
    };

    const getFilteredAssessments = () => {
        return assessments.filter(assessment => {
            const matchesRecommendation = filterRecommendation === 'all' || assessment.recommendation === filterRecommendation;
            const matchesConfidence = filterConfidence === 'all' || assessment.confidence_level === filterConfidence;
            const matchesSearch = searchQuery === '' ||
                assessment.opportunity_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                assessment.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
                assessment.assessed_by.toLowerCase().includes(searchQuery.toLowerCase());

            return matchesRecommendation && matchesConfidence && matchesSearch;
        });
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

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    const formatCurrency = (value: number, currency: string) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    const filteredAssessments = getFilteredAssessments();

    // Statistics
    const stats = {
        total: assessments.length,
        pursue: assessments.filter(a => a.recommendation === 'Pursue').length,
        caution: assessments.filter(a => a.recommendation === 'Caution').length,
        noBid: assessments.filter(a => a.recommendation === 'No-Bid').length,
        avgScore: assessments.length > 0
            ? Math.round(assessments.reduce((sum, a) => sum + a.weighted_score, 0) / assessments.length)
            : 0
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-gray-50">
            <TopBar title="Leadership Governance Dashboard" />

            <div className="flex-1 overflow-auto p-6">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Award className="text-orange-500" size={28} />
                        Submitted Assessments for Review
                    </h1>
                    <p className="text-sm text-gray-600 mt-1">
                        Review and approve bid qualification assessments submitted by Solution Architects
                    </p>
                </div>

                {/* Statistics Cards */}
                <div className="grid grid-cols-5 gap-4 mb-6">
                    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide">Total Submitted</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
                            </div>
                            <FileText className="text-blue-500" size={24} />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide">Pursue</p>
                                <p className="text-2xl font-bold text-green-600 mt-1">{stats.pursue}</p>
                            </div>
                            <CheckCircle className="text-green-500" size={24} />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide">Caution</p>
                                <p className="text-2xl font-bold text-yellow-600 mt-1">{stats.caution}</p>
                            </div>
                            <AlertCircle className="text-yellow-500" size={24} />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide">No-Bid</p>
                                <p className="text-2xl font-bold text-red-600 mt-1">{stats.noBid}</p>
                            </div>
                            <AlertCircle className="text-red-500" size={24} />
                        </div>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide">Avg Score</p>
                                <p className="text-2xl font-bold text-blue-600 mt-1">{stats.avgScore}</p>
                            </div>
                            <TrendingUp className="text-blue-500" size={24} />
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search by opportunity, customer, or SA..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <select
                            value={filterRecommendation}
                            onChange={(e) => setFilterRecommendation(e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">All Recommendations</option>
                            <option value="Pursue">Pursue</option>
                            <option value="Caution">Caution</option>
                            <option value="No-Bid">No-Bid</option>
                        </select>

                        <select
                            value={filterConfidence}
                            onChange={(e) => setFilterConfidence(e.target.value)}
                            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">All Confidence Levels</option>
                            <option value="High">High Confidence</option>
                            <option value="Medium">Medium Confidence</option>
                            <option value="Low">Low Confidence</option>
                        </select>
                    </div>
                </div>

                {/* Assessments Table */}
                <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
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
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                                        Loading assessments...
                                    </td>
                                </tr>
                            ) : filteredAssessments.length === 0 ? (
                                <tr>
                                    <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                                        No assessments found matching your filters
                                    </td>
                                </tr>
                            ) : (
                                filteredAssessments.map((assessment) => (
                                    <tr
                                        key={assessment.id}
                                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                                        onClick={() => navigate(`/opportunity/${assessment.opp_id}`)}
                                    >
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
                                            <span className={`text-lg font-bold ${getScoreColor(assessment.weighted_score)}`}>
                                                {assessment.weighted_score}
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
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/opportunity/${assessment.opp_id}`);
                                                }}
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

                {/* Summary */}
                <div className="mt-4 text-sm text-gray-600">
                    Showing {filteredAssessments.length} of {assessments.length} submitted assessments
                </div>
            </div>
        </div>
    );
};
