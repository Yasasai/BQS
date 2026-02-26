import { API_URL } from '../config';
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { useAuth } from '../context/AuthContext';
import { TopBar } from '../components/TopBar';
import { ChevronLeft, FileText, TrendingUp, History, File } from 'lucide-react';

type TabType = 'overview' | 'score' | 'versions' | 'documents';

interface AssessmentHistoryItem {
    version: number;
    status: string;
    score: number;
    recommendation: string;
    summary: string;
    attachment_name?: string;
    created_at: string;
    created_by: string;
}

export function OpportunityDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<TabType>('overview');

    const isSA = user?.role === 'SA';
    const isSP = user?.role === 'SP';
    const canSeeScore = isSA || isSP;

    const [history, setHistory] = useState<AssessmentHistoryItem[]>([]);

    useEffect(() => {
        if (id) {
            fetchOpportunityDetail(id);
            fetchHistory(id);
        }
    }, [id]);

    const fetchOpportunityDetail = (oppId: string) => {
        setLoading(true);
        fetch(``${API_URL}`/opportunities/${oppId}`)
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

    const fetchHistory = (oppId: string) => {
        fetch(``${API_URL}`/scoring/${oppId}/history`)
            .then(res => res.json())
            .then(data => setHistory(data))
            .catch(err => console.error("Failed to fetch history", err));
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
                    {opportunity.remote_url && (
                        <a
                            href={opportunity.remote_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                        >
                            Open in Oracle CRM
                            <FileText size={14} />
                        </a>
                    )}
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
                        {canSeeScore && (
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
                        )}
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
                    </div >
                </div >

                {/* Content Area */}
                <div className="flex-1 p-6">
                    {activeTab === 'overview' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                            <h3 className="text-lg font-bold text-gray-800 border-b pb-2 mb-6">Opportunity Information</h3>
                            <div className="grid grid-cols-2 gap-x-16 gap-y-6">
                                {/* Left Column */}
                                <div className="space-y-6">
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Opportunity Number
                                        </label>
                                        <p className="text-[13px] text-gray-900 font-medium">
                                            {opportunity.remote_id}
                                        </p>
                                        {opportunity.remote_url && (
                                            <a
                                                href={opportunity.remote_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-[11px] text-blue-600 hover:underline flex items-center gap-1 mt-1 font-semibold"
                                            >
                                                Source API Link
                                            </a>
                                        )}
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Owner
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">
                                            {opportunity.sales_owner || '-'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Name
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1 font-semibold">
                                            {opportunity.name}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Account (Customer)
                                        </label>
                                        <p className="text-[13px] text-blue-600 font-semibold border-b border-gray-100 pb-1">
                                            {opportunity.customer}
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                                GEO
                                            </label>
                                            <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">{opportunity.geo || 'MEA'}</p>
                                        </div>
                                        <div>
                                            <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                                Region
                                            </label>
                                            <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">{opportunity.region || 'MEA - Dubai'}</p>
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Sector
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">
                                            {opportunity.sector || 'Others'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Practice
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">
                                            {opportunity.practice || 'MSSP -Cybersecurity'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Solution Architect
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1 font-medium bg-blue-50/50 px-2 py-1 rounded italic">
                                            {opportunity.assigned_sa || 'NA'}
                                        </p>
                                    </div>
                                </div>

                                {/* Right Column */}
                                <div className="space-y-6">
                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Sales Stage
                                        </label>
                                        <p className="text-[13px] text-gray-900 font-medium">
                                            {opportunity.stage || 'Bid Preparation'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Win Probability (%)
                                        </label>
                                        <p className="text-[13px] text-gray-900 font-bold text-lg text-blue-700">
                                            {opportunity.win_probability || '40'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Currency
                                        </label>
                                        <p className="text-[13px] text-gray-900">{opportunity.currency || 'AED'}</p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Estimated Billing Date
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1">
                                            {opportunity.estimated_billing_date || '27-Nov-2025'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Expected PO Receive Date
                                        </label>
                                        <p className="text-[13px] text-gray-900 border-b border-gray-100 pb-1 font-semibold text-blue-800">
                                            {opportunity.expected_po_date || '29-Oct-2025'}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                                            Deal Amount
                                        </label>
                                        <p className="text-xl font-bold text-gray-900">
                                            {new Intl.NumberFormat('en-US', {
                                                style: 'currency',
                                                currency: opportunity.currency || 'AED',
                                                maximumFractionDigits: 0
                                            }).format(opportunity.deal_value || 500000)}
                                        </p>
                                    </div>

                                    <div className="pt-4">
                                        <div className="bg-gray-50 p-4 rounded-md border border-gray-100">
                                            <label className="block text-[10px] font-bold text-gray-400 uppercase mb-2">Internal Status</label>
                                            <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-bold uppercase tracking-tighter">
                                                {opportunity.status || 'NEW FROM CRM'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
                    }

                    {
                        activeTab === 'score' && (
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
                        )
                    }

                    {activeTab === 'versions' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            {history.length === 0 ? (
                                <div className="text-center py-12">
                                    <History size={48} className="mx-auto text-gray-400 mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Version History</h3>
                                    <p className="text-sm text-gray-600">
                                        No previous versions available.
                                    </p>
                                </div>
                            ) : (
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">Assessment History</h3>
                                    <div className="overflow-x-auto">
                                        <table className="min-w-full divide-y divide-gray-200">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Submitted By</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                                </tr>
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-200">
                                                {history.map((h, idx) => (
                                                    <tr key={idx}>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">v{h.version}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(h.created_at).toLocaleString()}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{h.created_by}</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">{h.score}%</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                                                ${h.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                                                                    h.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                                                                        'bg-yellow-100 text-yellow-800'}`}>
                                                                {h.status}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'documents' && (
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            {history.filter(h => h.attachment_name).length === 0 ? (
                                <div className="text-center py-12">
                                    <File size={48} className="mx-auto text-gray-400 mb-4" />
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Documents</h3>
                                    <p className="text-sm text-gray-600 mb-6">
                                        No documents have been uploaded for this opportunity.
                                    </p>
                                </div>
                            ) : (
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">Uploaded Documents</h3>
                                    <div className="space-y-4">
                                        {history.filter(h => h.attachment_name).map((h, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                                                <div className="flex items-center gap-3">
                                                    <div className="bg-blue-100 p-2 rounded">
                                                        <FileText className="text-blue-600" size={20} />
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium text-gray-900">{h.attachment_name}</p>
                                                        <p className="text-xs text-gray-500">
                                                            Uploaded in Version {h.version} by {h.created_by} on {new Date(h.created_at).toLocaleDateString()}
                                                        </p>
                                                    </div>
                                                </div>
                                                <a
                                                    href={`#`} // Ideally link to actual file download if API supported
                                                    className="text-sm text-blue-600 font-medium hover:underline"
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        alert(`Downloading ${h.attachment_name}... (Mock Action)`);
                                                    }}
                                                >
                                                    Download
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div >
            </div >
        </div >
    );
}
