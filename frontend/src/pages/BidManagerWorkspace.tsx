import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Building2,
    ChevronRight,
    UploadCloud,
    FileText,
    Info,
    LayoutDashboard,
    Save,
    Send,
    TrendingUp,
    Users,
    Target,
    DollarSign,
    Percent,
    CheckCircle2,
    AlertCircle,
    X,
    Plus,
    ArrowLeft,
    Briefcase,
    MapPin,
    BarChart3,
    Calendar,
    User as UserIcon,
    ShieldCheck,
    Scale,
    Lock,
    Archive,
    Layers,
    ThumbsUp,
    ThumbsDown
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Opportunity } from '../types';

interface DocumentCategory {
    category_id: string;
    label_name: string;
}

interface ScoringSection {
    section_code: string;
    section_name: string;
    weight: number;
    display_order: number;
    reasons: Record<string, string[]>;
}

interface SectionValue {
    section_code: string;
    score: number;
    notes: string;
    selected_reasons: string[];
}

interface UploadedFile {
    id: string;
    name: string;
    category: string;
    status: 'uploading' | 'completed' | 'error';
}

export const BidManagerWorkspace: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { authFetch, user } = useAuth();
    const isBM = user?.role === 'BM';

    // State
    const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
    const [sections, setSections] = useState<ScoringSection[]>([]);
    const [sectionValues, setSectionValues] = useState<Record<string, SectionValue>>({});
    const [categories, setCategories] = useState<DocumentCategory[]>([]);
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [activeTab, setActiveTab] = useState<'assessment' | 'team' | 'current-assignments' | 'closed'>('assessment');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [recommendation, setRecommendation] = useState<string | null>(null);
    const [showCloseModal, setShowCloseModal] = useState(false);
    const [closeReason, setCloseReason] = useState<'WON' | 'LOST'>('WON');
    const [closing, setClosing] = useState(false);
    const [bmOpportunities, setBmOpportunities] = useState<any[]>([]);
    const [loadingBmList, setLoadingBmList] = useState(false);

    const isClosed = opportunity?.workflow_status === 'CLOSED';
    const isReadOnly = !isBM || isClosed;

    // Financials state (synced with opportunity but editable)
    const [financials, setFinancials] = useState({
        deal_value: 0,
        margin_percentage: 0
    });

    // Team state (IDs)
    const [team, setTeam] = useState({
        practice_head_ids: [] as string[],
        sa_ids: [] as string[],
        sales_head: '',
        sp: '',
        legal: '',
        finance: ''
    });

    // User lists for dropdowns
    const [usersList, setUsersList] = useState<Record<string, any[]>>({
        PH: [],
        SA: [],
        SH: [],
        SP: [],
        LEGAL: [],
        FINANCE: []
    });

    // Fetch Initial Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);

                // Parallel fetching for core data
                const [oppRes, configRes, catRes] = await Promise.all([
                    authFetch(`/api/opportunities/${id}`),
                    authFetch(`/api/scoring/config`),
                    authFetch(`/api/opportunities/document-categories`)
                ]);

                if (oppRes.ok) {
                    const oppData = await oppRes.json();
                    setOpportunity(oppData);
                    setFinancials({
                        deal_value: oppData.deal_value || 0,
                        margin_percentage: oppData.margin_percentage || 0
                    });
                    setTeam({
                        practice_head_ids: oppData.assigned_practice_head_ids || [],
                        sa_ids: oppData.assigned_sa_ids || [],
                        sales_head: oppData.assigned_sales_head_id || '',
                        sp: oppData.assigned_sp_id || '',
                        legal: oppData.assigned_legal_id || '',
                        finance: oppData.assigned_finance_id || ''
                    });
                }

                if (configRes.ok) {
                    const configData = await configRes.json();
                    setSections(configData);

                    // Fetch latest score values if they exist
                    const scoreRes = await authFetch(`/api/scoring/${id}/latest`);
                    if (scoreRes.ok) {
                        const scoreData = await scoreRes.json();
                        if (scoreData.sections && scoreData.sections.length > 0) {
                            const vals: Record<string, SectionValue> = {};
                            scoreData.sections.forEach((s: any) => {
                                vals[s.section_code] = {
                                    section_code: s.section_code,
                                    score: s.score || 1.0,
                                    notes: s.notes || '',
                                    selected_reasons: s.selected_reasons || []
                                };
                            });
                            setSectionValues(vals);
                            if (scoreData.recommendation) setRecommendation(scoreData.recommendation);
                        } else {
                            // Initialize with default values
                            const initialVals: Record<string, SectionValue> = {};
                            configData.forEach((s: any) => {
                                initialVals[s.section_code] = {
                                    section_code: s.section_code,
                                    score: 1.0,
                                    notes: '',
                                    selected_reasons: []
                                };
                            });
                            setSectionValues(initialVals);
                        }
                    }
                }

                if (catRes.ok) {
                    const catData = await catRes.json();
                    if (catData && catData.length > 0) {
                        setCategories(catData);
                    } else {
                        console.warn("⚠️ API returned empty categories, using fallbacks.");
                        setCategories([
                            { category_id: 'rfp', label_name: 'RFP' },
                            { category_id: 'proposal', label_name: 'Proposal' },
                            { category_id: 'rls', label_name: 'RLS' },
                            { category_id: 'pricing', label_name: 'Pricing' },
                            { category_id: 'proxy', label_name: 'Proxy Evidence' }
                        ]);
                    }
                } else {
                    console.warn("⚠️ Document categories fetch failed, using fallbacks.");
                    setCategories([
                        { category_id: 'rfp', label_name: 'RFP' },
                        { category_id: 'proposal', label_name: 'Proposal' },
                        { category_id: 'rls', label_name: 'RLS' },
                        { category_id: 'pricing', label_name: 'Pricing' },
                        { category_id: 'proxy', label_name: 'Proxy Evidence' }
                    ]);
                }
            } catch (error) {
                console.error("❌ Error fetching core workspace data:", error);
                // Fallback categories if everything else failed
                setCategories([
                    { category_id: 'rfp', label_name: 'RFP' },
                    { category_id: 'proposal', label_name: 'Proposal' },
                    { category_id: 'rls', label_name: 'RLS' },
                    { category_id: 'pricing', label_name: 'Pricing' },
                    { category_id: 'proxy', label_name: 'Proxy Evidence' }
                ]);
            }

            // Task 1 Fix: Handle usersRes separately to avoid ReferenceError and crash
            try {
                const usersRes = await authFetch('/api/users/');
                if (usersRes.ok) {
                    const allUsers = await usersRes.json();
                    const grouped = {
                        PH: allUsers.filter((u: any) => u.roles.includes('PH')),
                        SA: allUsers.filter((u: any) => u.roles.includes('SA')),
                        SH: allUsers.filter((u: any) => u.roles.includes('SH')),
                        SP: allUsers.filter((u: any) => u.roles.includes('SP') || u.roles.includes('SL')),
                        LEGAL: allUsers.filter((u: any) => u.roles.includes('LEGAL') || u.roles.includes('LL') || u.roles.includes('PSH')),
                        FINANCE: allUsers.filter((u: any) => u.roles.includes('FINANCE') || u.roles.includes('GH'))
                    };
                    setUsersList(grouped);
                }
            } catch (error) {
                console.error("Error fetching users list:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id, authFetch]);

    // Live Score Calculation
    const liveScore = useMemo(() => {
        let totalWeightedScore = 0;
        let totalWeight = 0;

        sections.forEach(s => {
            const val = sectionValues[s.section_code];
            const score = val ? val.score : 0;
            totalWeightedScore += score * s.weight;
            totalWeight += 5.0 * s.weight; // Max possible score is 5.0
        });

        if (totalWeight === 0) return 0;
        return Math.round((totalWeightedScore / totalWeight) * 100);
    }, [sections, sectionValues]);

    // Handlers
    const handleScoreChange = (code: string, score: number) => {
        setSectionValues(prev => ({
            ...prev,
            [code]: { ...prev[code], score }
        }));
    };

    const handleFileUpload = async (files: FileList | null) => {
        if (!files) return;

        const newFiles = Array.from(files).map(f => ({
            id: Math.random().toString(36).substr(2, 9),
            name: f.name,
            category: categories[0]?.category_id || '',
            status: 'uploading' as const
        }));

        setUploadedFiles(prev => [...prev, ...newFiles]);

        // Simulate/Perform upload
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await authFetch(`/api/upload`, {
                    method: 'POST',
                    body: formData
                });

                if (res.ok) {
                    setUploadedFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: 'completed' } : f));
                } else {
                    setUploadedFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: 'error' } : f));
                }
            } catch (e) {
                setUploadedFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: 'error' } : f));
            }
        }
    };

    const handleSave = async (submit = false) => {
        setSaving(true);
        try {
            const endpoint = submit ? `/api/scoring/${id}/submit` : `/api/scoring/${id}/draft`;
            const payload = {
                sections: Object.values(sectionValues),
                financials,
                team: {
                    assigned_practice_head_ids: team.practice_head_ids,
                    assigned_sa_ids: team.sa_ids,
                    assigned_sales_head_id: team.sales_head,
                    assigned_sp_id: team.sp,
                    assigned_finance_id: team.finance,
                    assigned_legal_id: team.legal
                }
            };

            // Call the explicit assign endpoint to update PH/SA/Team lists
            await authFetch(`/api/opportunities/${id}/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    assigned_practice_head_ids: team.practice_head_ids,
                    assigned_sa_ids: team.sa_ids,
                    assigned_sales_head_id: team.sales_head,
                    assigned_sp_id: team.sp,
                    assigned_finance_id: team.finance,
                    assigned_legal_id: team.legal
                })
            });

            const res = await authFetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert(submit ? "Assessment submitted successfully!" : "Draft saved successfully!");
                if (submit) navigate('/dashboard');
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail || 'Failed to save'}`);
            }
        } catch (error) {
            console.error("Save error:", error);
        } finally {
            setSaving(false);
        }
    };

    const handleClose = async () => {
        setClosing(true);
        try {
            const res = await authFetch(`/api/opportunities/${id}/close`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ close_reason: closeReason })
            });
            if (res.ok) {
                const updated = await authFetch(`/api/opportunities/${id}`);
                if (updated.ok) setOpportunity(await updated.json());
                setShowCloseModal(false);
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail || 'Failed to close opportunity'}`);
            }
        } catch (e) {
            console.error('Close error:', e);
        } finally {
            setClosing(false);
        }
    };

    const handleTabChange = async (tab: typeof activeTab) => {
        setActiveTab(tab);
        if ((tab === 'current-assignments' || tab === 'closed') && bmOpportunities.length === 0) {
            setLoadingBmList(true);
            try {
                const res = await authFetch(`/api/opportunities/?limit=50&page=1`);
                if (res.ok) {
                    const data = await res.json();
                    setBmOpportunities(data.opportunities || data.items || []);
                }
            } catch (e) {
                console.error('BM list fetch error:', e);
            } finally {
                setLoadingBmList(false);
            }
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-50 text-slate-900">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
        </div>
    );

    if (!opportunity) return <div>Opportunity not found</div>;

    return (
        <div className="flex flex-col h-screen bg-slate-50 text-slate-900 font-sans">
            {/* Task 1: Sticky Global Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate(-1)}
                        className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </button>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-bold tracking-widest text-indigo-600 uppercase">Opportunity Workspace</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-xs font-medium text-slate-500">#{opportunity.remote_id}</span>
                        </div>
                        <h1 className="text-xl font-bold text-slate-900 truncate max-w-md">{opportunity.name}</h1>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase tracking-tighter text-slate-400 font-bold mb-1">Workflow Status</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${
                            opportunity.workflow_status === 'CLOSED' ? 'bg-slate-100 text-slate-600 border-slate-300' :
                            opportunity.workflow_status === 'REOPENED' ? 'bg-amber-50 text-amber-600 border-amber-200' :
                            opportunity.workflow_status === 'ACTIVE' ? 'bg-indigo-50 text-indigo-600 border-indigo-200' :
                            opportunity.workflow_status === 'OPEN' ? 'bg-sky-50 text-sky-600 border-sky-200' :
                            'bg-slate-50 text-slate-500 border-slate-200'
                        }`}>
                            {opportunity.workflow_status === 'CLOSED' && <Lock className="w-3 h-3" />}
                            {opportunity.workflow_status?.replace(/_/g, ' ')}
                        </span>
                    </div>

                    <div className="h-10 w-px bg-slate-200"></div>

                    <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase tracking-tighter text-slate-400 font-bold mb-1">Live Score</span>
                        <div className="flex items-center gap-2">
                            <span className={`text-2xl font-black ${liveScore > 75 ? 'text-emerald-600' : liveScore > 50 ? 'text-amber-600' : 'text-rose-600'
                                }`}>{liveScore}%</span>
                        </div>
                    </div>

                    {recommendation && (
                        <>
                            <div className="h-10 w-px bg-slate-200"></div>
                            <div className="flex flex-col items-end">
                                <span className="text-[10px] uppercase tracking-tighter text-slate-400 font-bold mb-1">Recommendation</span>
                                <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${
                                    recommendation === 'GO'
                                        ? 'bg-emerald-50 text-emerald-600 border-emerald-200'
                                        : 'bg-rose-50 text-rose-600 border-rose-200'
                                }`}>
                                    {recommendation === 'GO' ? <ThumbsUp className="w-3 h-3" /> : <ThumbsDown className="w-3 h-3" />}
                                    {recommendation === 'GO' ? 'GO' : 'NO GO'}
                                </span>
                            </div>
                        </>
                    )}
                </div>
            </header>

            {/* Main Workspace Layout */}
            <main className="flex flex-1 overflow-hidden">
                {/* Task 2: Left Pane (Context & Collation) - 40% Width */}
                <aside className="w-[40%] border-r border-slate-200 bg-slate-50 overflow-y-auto custom-scrollbar p-6">
                    <div className="space-y-6">
                        {/* CRM Snapshot */}
                        <section className="bg-white border border-gray-200 shadow-sm rounded-2xl p-5">
                            <div className="flex items-center gap-2 mb-4">
                                <Target className="w-4 h-4 text-indigo-600" />
                                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">CRM Snapshot</h2>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="text-[10px] uppercase text-slate-400 font-bold mb-1">Customer</div>
                                    <div className="text-sm font-semibold text-slate-700">{opportunity.customer_name}</div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="text-[10px] uppercase text-slate-400 font-bold mb-1">Geography</div>
                                    <div className="text-sm font-semibold text-slate-700">{opportunity.geo || 'Global'}</div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="text-[10px] uppercase text-slate-400 font-bold mb-1">Sales Stage</div>
                                    <div className="text-sm font-semibold text-slate-700">{(opportunity as any).sales_stage || opportunity.stage}</div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                    <div className="text-[10px] uppercase text-slate-400 font-bold mb-1">Deal Value</div>
                                    <div className="text-sm font-bold text-indigo-600">
                                        {new Intl.NumberFormat('en-US', { style: 'currency', currency: opportunity.currency || 'USD' }).format(opportunity.deal_value)}
                                    </div>
                                </div>
                            </div>
                        </section>

                        <hr className="border-slate-200" />

                        {/* Document Upload */}
                        <section className="bg-white border border-gray-200 shadow-sm rounded-2xl p-5">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-indigo-600" />
                                    <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Solution Evidence</h2>
                                </div>
                                <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded uppercase font-bold">Audit Ready</span>
                            </div>

                            <div
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={(e) => {
                                    if (isReadOnly) return;
                                    e.preventDefault();
                                    handleFileUpload(e.dataTransfer.files);
                                }}
                                className="border-2 border-dashed border-slate-200 rounded-2xl p-8 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 hover:border-indigo-400 transition-all cursor-pointer group"
                                onClick={() => !isReadOnly && document.getElementById('file-upload')?.click()}
                            >
                                <input
                                    type="file"
                                    id="file-upload"
                                    className="hidden"
                                    multiple
                                    onChange={(e) => handleFileUpload(e.target.files)}
                                    disabled={isReadOnly}
                                />
                                <div className="w-12 h-12 bg-indigo-50 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                    <UploadCloud className="w-6 h-6 text-indigo-600" />
                                </div>
                                <p className="text-sm font-medium text-slate-700">Drag & drop files or <span className="text-indigo-600">browse</span></p>
                                <p className="text-xs text-slate-500 mt-1">RFP, Proposal, or Architecture documents</p>
                            </div>

                            {/* Uploaded Files List */}
                            <div className="mt-4 space-y-3">
                                {uploadedFiles.map(file => (
                                    <div key={file.id} className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex items-center justify-between gap-3 animate-in fade-in slide-in-from-left-2 transition-all">
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className="w-8 h-8 bg-white border border-slate-200 rounded flex items-center justify-center shrink-0">
                                                {file.status === 'uploading' ? (
                                                    <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                                                ) : (
                                                    <FileText className="w-4 h-4 text-slate-400" />
                                                )}
                                            </div>
                                            <div className="overflow-hidden">
                                                <div className="text-xs font-medium text-slate-700 truncate">{file.name}</div>
                                                <div className="text-[10px] text-slate-500">2.4 MB</div>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <select
                                                value={file.category}
                                                onChange={(e) => {
                                                    setUploadedFiles(prev => prev.map(f => f.id === file.id ? { ...f, category: e.target.value } : f));
                                                }}
                                                className="bg-white border border-slate-200 rounded px-2 py-1 text-[10px] text-slate-600 focus:outline-none focus:border-indigo-500"
                                            >
                                                {categories.map(cat => (
                                                    <option key={cat.category_id} value={cat.category_id}>{cat.label_name}</option>
                                                ))}
                                            </select>
                                            <button
                                                onClick={() => setUploadedFiles(prev => prev.filter(f => f.id !== file.id))}
                                                className="p-1 hover:bg-rose-50 hover:text-rose-600 rounded transition-colors"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>
                </aside>

                {/* Task 3: Right Pane (Action & Assessment) - 60% Width */}
                <section className="w-[60%] flex flex-col relative h-full bg-slate-100">
                    {/* Tabs Navigation */}
                    <div className="flex bg-white border-b border-slate-200 px-6 pt-2 overflow-x-auto">
                        {[
                            { key: 'assessment', icon: <BarChart3 className="w-4 h-4" />, label: '9-Factor Assessment' },
                            { key: 'team', icon: <Users className="w-4 h-4" />, label: 'Team & Financials' },
                            { key: 'current-assignments', icon: <Layers className="w-4 h-4" />, label: 'Current Assignments' },
                            { key: 'closed', icon: <Archive className="w-4 h-4" />, label: 'Closed' },
                        ].map(tab => (
                            <button
                                key={tab.key}
                                onClick={() => handleTabChange(tab.key as typeof activeTab)}
                                className={`flex items-center gap-2 px-5 py-3 text-sm font-bold transition-all relative whitespace-nowrap ${
                                    activeTab === tab.key ? 'text-indigo-600' : 'text-slate-400 hover:text-slate-600'
                                }`}
                            >
                                {tab.icon}
                                {tab.label}
                                {activeTab === tab.key && (
                                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 animate-in fade-in zoom-in-95"></div>
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 overflow-y-auto p-6 pb-24 custom-scrollbar bg-slate-100">
                        {activeTab === 'current-assignments' ? (
                            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                                    <Layers className="w-5 h-5 text-indigo-600" /> My Active Assignments
                                </h3>
                                {loadingBmList ? (
                                    <div className="flex justify-center py-12">
                                        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600"></div>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {bmOpportunities.filter(o => o.workflow_status !== 'CLOSED').length === 0 ? (
                                            <p className="text-sm text-slate-500 italic text-center py-12">No active assignments.</p>
                                        ) : bmOpportunities.filter(o => o.workflow_status !== 'CLOSED').map((opp: any) => (
                                            <div
                                                key={opp.id}
                                                onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                className={`bg-white border rounded-xl p-4 cursor-pointer hover:border-indigo-300 hover:shadow-sm transition-all ${opp.id === id ? 'border-indigo-400 ring-1 ring-indigo-200' : 'border-slate-200'}`}
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="min-w-0">
                                                        <p className="text-sm font-bold text-slate-800 truncate">{opp.name}</p>
                                                        <p className="text-xs text-slate-500 mt-0.5">{opp.customer_name} · #{opp.remote_id}</p>
                                                    </div>
                                                    <span className="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                                                        {opp.workflow_status}
                                                    </span>
                                                </div>
                                                <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-400">
                                                    <span>{new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', notation: 'compact' }).format(opp.deal_value)}</span>
                                                    <span>·</span>
                                                    <span>{opp.geo || 'Global'}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : activeTab === 'closed' ? (
                            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
                                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                                    <Archive className="w-5 h-5 text-slate-500" /> Closed Opportunities
                                </h3>
                                {loadingBmList ? (
                                    <div className="flex justify-center py-12">
                                        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600"></div>
                                    </div>
                                ) : (
                                    <div className="space-y-3">
                                        {bmOpportunities.filter(o => o.workflow_status === 'CLOSED').length === 0 ? (
                                            <p className="text-sm text-slate-500 italic text-center py-12">No closed opportunities.</p>
                                        ) : bmOpportunities.filter(o => o.workflow_status === 'CLOSED').map((opp: any) => (
                                            <div
                                                key={opp.id}
                                                onClick={() => navigate(`/opportunity/${opp.id}`)}
                                                className="bg-white border border-slate-200 rounded-xl p-4 cursor-pointer hover:border-slate-300 hover:shadow-sm transition-all"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="min-w-0">
                                                        <p className="text-sm font-bold text-slate-700 truncate">{opp.name}</p>
                                                        <p className="text-xs text-slate-500 mt-0.5">{opp.customer_name} · #{opp.remote_id}</p>
                                                    </div>
                                                    <span className={`shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                                                        opp.close_reason === 'WON' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-rose-50 text-rose-600 border-rose-200'
                                                    }`}>
                                                        {opp.close_reason || 'CLOSED'}
                                                    </span>
                                                </div>
                                                <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-400">
                                                    <span>{new Intl.NumberFormat('en-US', { style: 'currency', currency: opp.currency || 'USD', notation: 'compact' }).format(opp.deal_value)}</span>
                                                    <span>·</span>
                                                    <span>{opp.geo || 'Global'}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : activeTab === 'assessment' ? (
                            <div className="space-y-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-bold text-slate-900">Scoring Criteria</h3>
                                    <div className="text-xs text-slate-500 italic">Drag to adjust or click to select value</div>
                                </div>

                                <div className="grid gap-4">
                                    {sections.map((section) => {
                                        const currentVal = sectionValues[section.section_code] || { score: 1.0, notes: '' };
                                        return (
                                            <div key={section.section_code} className="bg-white rounded-2xl border border-slate-200 p-6 hover:border-indigo-200 shadow-sm transition-all group">
                                                <div className="flex items-start justify-between mb-4">
                                                    <div>
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <h4 className="font-bold text-slate-800">{section.section_name}</h4>
                                                            <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-bold">Weight: x{section.weight}</span>
                                                        </div>
                                                        <p className="text-xs text-slate-500">Evaluate based on {section.section_name.toLowerCase()} standards</p>
                                                    </div>
                                                    <div className={`text-2xl font-black ${currentVal.score >= 4 ? 'text-emerald-600' : currentVal.score >= 2.5 ? 'text-amber-600' : 'text-rose-600'
                                                        }`}>
                                                        {currentVal.score.toFixed(1)}
                                                    </div>
                                                </div>

                                                {/* Custom 1-5 Slider */}
                                                <div className="relative h-12 flex items-center">
                                                    <div className="absolute inset-0 flex justify-between px-1">
                                                        {[1, 2, 3, 4, 5].map(n => (
                                                            <div key={n} className="flex flex-col items-center justify-center">
                                                                <div className="h-2 w-px bg-slate-200 mb-1"></div>
                                                                <span className="text-[10px] font-bold text-slate-400">{n}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    <input
                                                        type="range"
                                                        min="1.0"
                                                        max="5.0"
                                                        step="0.5"
                                                        value={currentVal.score}
                                                        onChange={(e) => handleScoreChange(section.section_code, parseFloat(e.target.value))}
                                                        className="w-full appearance-none bg-slate-200 h-2 rounded-full cursor-pointer accent-indigo-600 z-10 relative"
                                                        disabled={isReadOnly}
                                                    />
                                                </div>

                                                <div className="mt-4">
                                                    <textarea
                                                        placeholder="Add justification notes..."
                                                        value={currentVal.notes}
                                                        onChange={(e) => {
                                                            const val = e.target.value;
                                                            setSectionValues(prev => ({
                                                                ...prev,
                                                                [section.section_code]: { ...prev[section.section_code], notes: val }
                                                            }));
                                                        }}
                                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-indigo-400 min-h-[80px] transition-all"
                                                        disabled={isReadOnly}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                                {/* Task 3: Team & Financials Content */}
                                <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                                    <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                                        <DollarSign className="w-5 h-5 text-indigo-600" />
                                        Deal Financials
                                    </h3>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Revenue (Deal Value)</label>
                                            <div className="relative">
                                                <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                                <input
                                                    type="number"
                                                    value={financials.deal_value}
                                                    onChange={(e) => setFinancials(prev => ({ ...prev, deal_value: parseFloat(e.target.value) || 0 }))}
                                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 text-slate-900 font-bold focus:outline-none focus:border-indigo-500 transition-all"
                                                    disabled={isReadOnly}
                                                />
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Margin Percentage (PAT)</label>
                                            <div className="relative">
                                                <Percent className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                                <input
                                                    type="number"
                                                    value={financials.margin_percentage}
                                                    onChange={(e) => setFinancials(prev => ({ ...prev, margin_percentage: parseFloat(e.target.value) || 0 }))}
                                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-4 text-slate-900 font-bold focus:outline-none focus:border-indigo-500 transition-all"
                                                    disabled={isReadOnly}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </section>

                                <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                                    <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                                        <Users className="w-5 h-5 text-indigo-600" />
                                        Pursuit Team Assignment
                                    </h3>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Practice Head</label>
                                            <div className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden max-h-[160px] overflow-y-auto">
                                                {usersList.PH.length === 0 ? (
                                                    <p className="text-xs text-slate-400 p-3 italic">No Practice Heads available</p>
                                                ) : usersList.PH.map(u => (
                                                    <label key={u.user_id} className={`flex items-center gap-3 px-4 py-2.5 border-b border-slate-100 last:border-0 transition-colors ${isReadOnly ? 'opacity-60' : 'hover:bg-slate-100 cursor-pointer'}`}>
                                                        <input
                                                            type="checkbox"
                                                            checked={team.practice_head_ids.includes(u.user_id)}
                                                            onChange={() => {
                                                                if (isReadOnly) return;
                                                                setTeam(prev => ({
                                                                    ...prev,
                                                                    practice_head_ids: prev.practice_head_ids.includes(u.user_id)
                                                                        ? prev.practice_head_ids.filter(id => id !== u.user_id)
                                                                        : [...prev.practice_head_ids, u.user_id]
                                                                }));
                                                            }}
                                                            disabled={isReadOnly}
                                                            className="w-4 h-4 rounded accent-indigo-600"
                                                        />
                                                        <span className="text-sm text-slate-700 font-medium">{u.display_name}</span>
                                                    </label>
                                                ))}
                                            </div>
                                            {team.practice_head_ids.length > 0 && (
                                                <p className="text-[10px] text-indigo-500 font-medium">{team.practice_head_ids.length} selected</p>
                                            )}
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Solution Architect</label>
                                            <div className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden max-h-[160px] overflow-y-auto">
                                                {usersList.SA.length === 0 ? (
                                                    <p className="text-xs text-slate-400 p-3 italic">No Solution Architects available</p>
                                                ) : usersList.SA.map(u => (
                                                    <label key={u.user_id} className={`flex items-center gap-3 px-4 py-2.5 border-b border-slate-100 last:border-0 transition-colors ${isReadOnly ? 'opacity-60' : 'hover:bg-slate-100 cursor-pointer'}`}>
                                                        <input
                                                            type="checkbox"
                                                            checked={team.sa_ids.includes(u.user_id)}
                                                            onChange={() => {
                                                                if (isReadOnly) return;
                                                                setTeam(prev => ({
                                                                    ...prev,
                                                                    sa_ids: prev.sa_ids.includes(u.user_id)
                                                                        ? prev.sa_ids.filter(id => id !== u.user_id)
                                                                        : [...prev.sa_ids, u.user_id]
                                                                }));
                                                            }}
                                                            disabled={isReadOnly}
                                                            className="w-4 h-4 rounded accent-indigo-600"
                                                        />
                                                        <span className="text-sm text-slate-700 font-medium">{u.display_name}</span>
                                                    </label>
                                                ))}
                                            </div>
                                            {team.sa_ids.length > 0 && (
                                                <p className="text-[10px] text-indigo-500 font-medium">{team.sa_ids.length} selected</p>
                                            )}
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Sales Head (SH)</label>
                                            <select
                                                value={team.sales_head}
                                                onChange={(e) => setTeam(prev => ({ ...prev, sales_head: e.target.value }))}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 text-slate-700 focus:outline-none focus:border-indigo-500 transition-all font-medium appearance-none"
                                                disabled={isReadOnly}
                                            >
                                                <option value="">Unassigned</option>
                                                {usersList.SH.map(u => <option key={u.user_id} value={u.user_id}>{u.display_name}</option>)}
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Sales Pursuit (SP)</label>
                                            <select
                                                value={team.sp}
                                                onChange={(e) => setTeam(prev => ({ ...prev, sp: e.target.value }))}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 text-slate-700 focus:outline-none focus:border-indigo-500 transition-all font-medium appearance-none"
                                                disabled={isReadOnly}
                                            >
                                                <option value="">Unassigned</option>
                                                {usersList.SP.map(u => <option key={u.user_id} value={u.user_id}>{u.display_name}</option>)}
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                                                <Scale className="w-3 h-3" /> Legal Lead
                                            </label>
                                            <select
                                                value={team.legal}
                                                onChange={(e) => setTeam(prev => ({ ...prev, legal: e.target.value }))}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 text-slate-700 focus:outline-none focus:border-indigo-500 transition-all font-medium appearance-none"
                                                disabled={isReadOnly}
                                            >
                                                <option value="">Select Legal Officer</option>
                                                {usersList.LEGAL.map(u => <option key={u.user_id} value={u.user_id}>{u.display_name}</option>)}
                                            </select>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                                                <ShieldCheck className="w-3 h-3" /> Finance Lead
                                            </label>
                                            <select
                                                value={team.finance}
                                                onChange={(e) => setTeam(prev => ({ ...prev, finance: e.target.value }))}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 px-4 text-slate-700 focus:outline-none focus:border-indigo-500 transition-all font-medium appearance-none"
                                                disabled={isReadOnly}
                                            >
                                                <option value="">Select Finance Controller</option>
                                                {usersList.FINANCE.map(u => <option key={u.user_id} value={u.user_id}>{u.display_name}</option>)}
                                            </select>
                                        </div>
                                    </div>

                                    <div className="mt-8 p-4 bg-indigo-50 border border-indigo-100 rounded-xl flex gap-3">
                                        <Info className="w-5 h-5 text-indigo-500 shrink-0" />
                                        <p className="text-xs text-slate-500 leading-relaxed">
                                            Assigning team members will trigger an email notification and add this opportunity to their personal dashboards. Approval flows will follow the standard matrix mapping.
                                        </p>
                                    </div>
                                </section>
                            </div>
                        )}
                    </div>

                    {/* Task 4: Bottom Floating Action Bar */}
                    <footer className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-slate-200 p-4 px-6 flex items-center justify-between z-40">
                        <div className="flex items-center gap-4">
                            <div className="flex -space-x-2">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-600">
                                        {String.fromCharCode(64 + i)}
                                    </div>
                                ))}
                                <div className="w-8 h-8 rounded-full border-2 border-white bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-400">
                                    <Plus className="w-3 h-3" />
                                </div>
                            </div>
                            <span className="text-xs text-slate-500 font-medium">3 active collaborators</span>
                        </div>

                        <div className="flex items-center gap-3">
                            {isClosed ? (
                                <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 text-slate-500 text-sm font-bold border border-slate-200">
                                    <Lock className="w-4 h-4" /> Read-Only — Opportunity Closed
                                </span>
                            ) : (
                                <>
                                    <button
                                        onClick={() => handleSave(false)}
                                        disabled={saving || isReadOnly}
                                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl border border-slate-200 font-bold text-sm text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all disabled:opacity-50"
                                    >
                                        <Save className="w-4 h-4" />
                                        Save Draft
                                    </button>
                                    <button
                                        onClick={() => handleSave(true)}
                                        disabled={saving || isReadOnly}
                                        className="flex items-center gap-2 px-8 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 font-bold text-sm text-white shadow-lg shadow-indigo-500/10 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50"
                                    >
                                        {saving ? (
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                        ) : (
                                            <Send className="w-4 h-4" />
                                        )}
                                        Submit Assessment
                                    </button>
                                    {isBM && (
                                        <button
                                            onClick={() => setShowCloseModal(true)}
                                            className="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-rose-200 text-rose-600 font-bold text-sm hover:bg-rose-50 transition-all"
                                        >
                                            <Archive className="w-4 h-4" />
                                            Close Opportunity
                                        </button>
                                    )}
                                </>
                            )}
                        </div>
                    </footer>
                </section>
            </main>

            {/* Close Opportunity Modal */}
            {showCloseModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md mx-4 animate-in fade-in zoom-in-95">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-rose-50 rounded-full flex items-center justify-center">
                                <Archive className="w-5 h-5 text-rose-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-bold text-slate-900">Close Opportunity</h2>
                                <p className="text-xs text-slate-500">This action is irreversible without Admin reopen.</p>
                            </div>
                        </div>

                        <p className="text-sm text-slate-600 mb-6">
                            Select the final outcome for <span className="font-bold text-slate-800">{opportunity?.name}</span>.
                        </p>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <button
                                onClick={() => setCloseReason('WON')}
                                className={`flex flex-col items-center gap-2 p-5 rounded-xl border-2 font-bold text-sm transition-all ${
                                    closeReason === 'WON'
                                        ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                                        : 'border-slate-200 text-slate-500 hover:border-emerald-200 hover:bg-emerald-50/50'
                                }`}
                            >
                                <ThumbsUp className="w-6 h-6" />
                                WON
                                <span className="text-[10px] font-normal">Bid was successful</span>
                            </button>
                            <button
                                onClick={() => setCloseReason('LOST')}
                                className={`flex flex-col items-center gap-2 p-5 rounded-xl border-2 font-bold text-sm transition-all ${
                                    closeReason === 'LOST'
                                        ? 'border-rose-400 bg-rose-50 text-rose-700'
                                        : 'border-slate-200 text-slate-500 hover:border-rose-200 hover:bg-rose-50/50'
                                }`}
                            >
                                <ThumbsDown className="w-6 h-6" />
                                LOST
                                <span className="text-[10px] font-normal">Bid was unsuccessful</span>
                            </button>
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setShowCloseModal(false)}
                                disabled={closing}
                                className="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-bold text-sm hover:bg-slate-50 transition-all disabled:opacity-50"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleClose}
                                disabled={closing}
                                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm text-white shadow-lg transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 ${
                                    closeReason === 'WON' ? 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20' : 'bg-rose-600 hover:bg-rose-700 shadow-rose-500/20'
                                }`}
                            >
                                {closing ? (
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <Archive className="w-4 h-4" />
                                )}
                                Confirm {closeReason}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #334155;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #475569;
        }
        
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 18px;
          width: 18px;
          border-radius: 50%;
          background: #6366f1;
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
          cursor: pointer;
        }
      `}</style>
        </div>
    );
};

export default BidManagerWorkspace;
