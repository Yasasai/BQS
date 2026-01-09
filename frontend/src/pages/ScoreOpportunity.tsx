import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Opportunity } from '../types';
import { TopBar } from '../components/TopBar';
import { ChevronLeft, Upload, Trash2, FileText } from 'lucide-react';

interface ScoringCriteria {
    id: string;
    name: string;
    score: number;
    notes: string;
}

interface Document {
    id: string;
    name: string;
    size: string;
    uploadedAt: string;
}

export function ScoreOpportunity() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Scoring criteria state
    const [criteria, setCriteria] = useState<ScoringCriteria[]>([
        {
            id: 'fit_strategic',
            name: 'Fit & Strategic Alignment',
            score: 3,
            notes: 'Opportunity aligns well with long-term strategic goals. Strong potential for market expansion in target segments.'
        },
        {
            id: 'capability_delivery',
            name: 'Capability & Delivery Readiness',
            score: 4,
            notes: 'Our team has strong expertise in the required technologies and a proven track record. Some minor resource planning needed.'
        },
        {
            id: 'commercial',
            name: 'Commercial Attractiveness',
            score: 3,
            notes: 'Good profit margin potential, but competitive pricing strategy will be required to win. Financials are solid.'
        },
        {
            id: 'risk_complexity',
            name: 'Risk & Complexity',
            score: 2,
            notes: 'Identified some technical challenges in integration, but manageable with current resources and a phased approach. Moderate project complexity.'
        }
    ]);

    const [documents, setDocuments] = useState<Document[]>([
        {
            id: '1',
            name: 'RFP_Document_v1.pdf',
            size: '2.5 MB',
            uploadedAt: '2024-01-05'
        },
        {
            id: '2',
            name: 'Client_Requirements.docx',
            size: '1.8 MB',
            uploadedAt: '2024-01-06'
        }
    ]);

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

    const handleScoreChange = (criteriaId: string, newScore: number) => {
        setCriteria(prev => prev.map(c =>
            c.id === criteriaId ? { ...c, score: newScore } : c
        ));
    };

    const handleNotesChange = (criteriaId: string, newNotes: string) => {
        setCriteria(prev => prev.map(c =>
            c.id === criteriaId ? { ...c, notes: newNotes } : c
        ));
    };

    const handleSaveDraft = async () => {
        setSaving(true);
        // TODO: Save to backend
        console.log('Saving draft...', criteria);
        setTimeout(() => {
            setSaving(false);
            alert('Draft saved successfully!');
        }, 1000);
    };

    const handleSubmit = async () => {
        setSaving(true);
        // TODO: Submit to backend
        console.log('Submitting assessment...', criteria);
        setTimeout(() => {
            setSaving(false);
            alert('Assessment submitted successfully!');
            navigate(-1);
        }, 1000);
    };

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files && files.length > 0) {
            // TODO: Upload to backend
            console.log('Uploading files...', files);
        }
    };

    const handleDeleteDocument = (docId: string) => {
        if (confirm('Are you sure you want to delete this document?')) {
            setDocuments(prev => prev.filter(d => d.id !== docId));
        }
    };

    const calculateAverageScore = () => {
        const total = criteria.reduce((sum, c) => sum + c.score, 0);
        return (total / criteria.length).toFixed(1);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
                <TopBar />
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-gray-500">Loading opportunity...</div>
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
                <div className="px-6 pt-4 pb-4 bg-white border-b border-gray-200">
                    <h1 className="text-2xl font-semibold text-gray-900">
                        Score Opportunity: {opportunity.remote_id || `OPP-${opportunity.id}`}
                    </h1>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        <span>Version: v2.3 (Draft)</span>
                        <span>•</span>
                        <span>Created: Aug 1, 2023 10:35 AM</span>
                        <span>•</span>
                        <span>Last Saved: Aug 1, 2023 10:35 AM</span>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 p-6">
                    <div className="grid grid-cols-3 gap-6">
                        {/* Left Column - Scoring Criteria (2/3 width) */}
                        <div className="col-span-2 space-y-4">
                            {criteria.map((criterion) => (
                                <div key={criterion.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex-1">
                                            <h3 className="text-base font-semibold text-gray-900 mb-2">
                                                {criterion.name}
                                            </h3>
                                            <div className="flex items-center gap-4">
                                                <span className="text-sm text-gray-600">Score (1-5)</span>
                                                <div className="flex-1 max-w-md">
                                                    <input
                                                        type="range"
                                                        min="0"
                                                        max="5"
                                                        step="1"
                                                        value={criterion.score}
                                                        onChange={(e) => handleScoreChange(criterion.id, parseInt(e.target.value))}
                                                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                                                    />
                                                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                                                        <span>0</span>
                                                        <span>1</span>
                                                        <span>2</span>
                                                        <span>3</span>
                                                        <span>4</span>
                                                        <span>5</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="ml-4">
                                            <div className="w-12 h-12 bg-blue-600 text-white rounded flex items-center justify-center text-xl font-bold">
                                                {criterion.score}
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Notes
                                        </label>
                                        <textarea
                                            value={criterion.notes}
                                            onChange={(e) => handleNotesChange(criterion.id, e.target.value)}
                                            rows={3}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                            placeholder="Add your notes here..."
                                        />
                                    </div>
                                </div>
                            ))}

                            {/* Average Score Display */}
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-base font-semibold text-gray-900">
                                        Average Score
                                    </span>
                                    <span className="text-2xl font-bold text-blue-600">
                                        {calculateAverageScore()} / 5.0
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Right Column - Version Documents (1/3 width) */}
                        <div className="col-span-1">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
                                <h3 className="text-base font-semibold text-gray-900 mb-4">
                                    Version Documents
                                </h3>

                                {/* Upload Area */}
                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 mb-4 text-center hover:border-blue-400 transition-colors">
                                    <Upload size={32} className="mx-auto text-gray-400 mb-2" />
                                    <p className="text-sm text-gray-600 mb-2">
                                        Drag & drop files here, or click to upload
                                    </p>
                                    <input
                                        type="file"
                                        multiple
                                        onChange={handleFileUpload}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <label
                                        htmlFor="file-upload"
                                        className="text-sm text-blue-600 hover:text-blue-700 cursor-pointer font-medium"
                                    >
                                        Browse files
                                    </label>
                                </div>

                                {/* Document List */}
                                <div className="space-y-2">
                                    {documents.map((doc) => (
                                        <div
                                            key={doc.id}
                                            className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100 transition-colors"
                                        >
                                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                                <FileText size={16} className="text-blue-600 flex-shrink-0" />
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-medium text-gray-900 truncate">
                                                        {doc.name}
                                                    </p>
                                                    <p className="text-xs text-gray-500">
                                                        {doc.size}
                                                    </p>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => handleDeleteDocument(doc.id)}
                                                className="text-red-600 hover:text-red-700 p-1"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    ))}
                                </div>

                                {/* Action Buttons */}
                                <div className="mt-6 space-y-2">
                                    <button
                                        onClick={handleSaveDraft}
                                        disabled={saving}
                                        className="w-full px-4 py-2 bg-white border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {saving ? 'Saving...' : 'Save Draft'}
                                    </button>
                                    <button
                                        onClick={handleSubmit}
                                        disabled={saving}
                                        className="w-full px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {saving ? 'Submitting...' : 'Submit / Confirm'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
