import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronLeft, FileText, TrendingUp, History, File } from 'lucide-react';

type TabType = 'overview' | 'score' | 'versions' | 'documents';

export function OpportunityDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('overview');

    useEffect(() => {
        if (id) {
            fetchOpportunityDetail(id);
        }
    }, [id]);

    const fetchOpportunityDetail = (oppId: string) => {
        setLoading(true);
        fetch(`http://localhost:8000/api/oracle-opportunity/${oppId}`)
            .then(res => res.json())
            .then(data => {
                setOpportunity(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch opportunity detail", err);
                setLoading(false);
            });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
                <TopBar />
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-gray-500">Loading opportunity details...</div>
                </div>
            </div>
        );
    }

    if (!opportunity) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
                <TopBar />
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-gray-500">Opportunity not found</div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
            <TopBar />

            <div className="flex flex-col flex-1">
                {/* Back Navigation */}
                <div className="px-6 pt-4 bg-white">
                    <button
                        onClick={() => navigate(-1)}
                        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                        <ChevronLeft size={16} />
                        Back
                    </button>
                </div>

                {/* Page Header */}
                <div className="px-6 pt-4 pb-6 bg-white border-b border-gray-200">
                    <h1 className="text-2xl font-semibold text-gray-900">
                        Opportunity Detail: {opportunity.remote_id || `OPP-${opportunity.id}`} - {opportunity.name}
                    </h1>
                </div>

                {/* Tabs */}
                <div className="px-6 bg-white border-b border-gray-200">
                    <div className="flex gap-6">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`flex items-center gap-2 px-1 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            <FileText size={16} />
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('score')}
                            className={`flex items-center gap-2 px-1 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'score'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            <TrendingUp size={16} />
                            Score
                        </button>
                        <button
                            onClick={() => setActiveTab('versions')}
                            className={`flex items-center gap-2 px-1 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'versions'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            <History size={16} />
                            Versions
                        </button>
                        <button
                            onClick={() => setActiveTab('documents')}
                            className={`flex items-center gap-2 px-1 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'documents'
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-600 hover:text-gray-900'
                                }`}
                        >
                            <File size={16} />
                            Documents
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 p-6">
                    {activeTab === 'overview' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="grid grid-cols-2 gap-x-12 gap-y-6">
                                {/* Left Column */}
                                <div className="space-y-6">
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Description
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.name}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Practice
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.practice || '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Deal Value
                                        </label>
                                        <p className="text-sm text-gray-900 font-medium">
                                            {new Intl.NumberFormat('en-US', {
                                                style: 'currency',
                                                currency: opportunity.currency || 'USD',
                                                maximumFractionDigits: 0
                                            }).format(opportunity.deal_value)}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Status
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.stage}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Proposal Submitted
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.rfp_date || '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            RFP Date
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.rfp_date || '2024-06-15'}
                                        </p>
                                    </div>
                                </div>

                                {/* Right Column */}
                                <div className="space-y-6">
                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Customer
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.customer}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Geo Region
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.geo || '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Sales Owner
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.sales_owner || '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Win Probability
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.win_probability ? `${opportunity.win_probability}%` : '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Last Updated
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {new Date(opportunity.last_synced_at).toLocaleString()}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                                            Close Date
                                        </label>
                                        <p className="text-sm text-gray-900">
                                            {opportunity.close_date || '-'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'score' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="text-center py-12">
                                <TrendingUp size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Assessment Score</h3>
                                <p className="text-sm text-gray-600 mb-6">
                                    No assessment has been completed for this opportunity yet.
                                </p>
                                <button
                                    onClick={() => navigate(`/score/${id}`)}
                                    className="bg-blue-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-blue-700 shadow-sm"
                                >
                                    Start Assessment
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'versions' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="text-center py-12">
                                <History size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Version History</h3>
                                <p className="text-sm text-gray-600">
                                    No previous versions available.
                                </p>
                            </div>
                        </div>
                    )}

                    {activeTab === 'documents' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="text-center py-12">
                                <File size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Documents</h3>
                                <p className="text-sm text-gray-600 mb-6">
                                    No documents have been uploaded for this opportunity.
                                </p>
                                <button className="bg-blue-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-blue-700 shadow-sm">
                                    Upload Document
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
