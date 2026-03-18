
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Save, Send, AlertTriangle, FileText, Upload, Trash2, CheckCircle, Edit3, RefreshCw, Hash } from 'lucide-react';
import { ApprovalModal } from '../components/ApprovalModal';
import apiClient from '../utils/apiClient';
import { API_ENDPOINTS } from '../constants/apiEndpoints';
import '../styles/Assessment.css';

const DEFAULT_CRITERIA = [
    { key: "STRAT", label: "Strategic Fit", weight: 0.15 },
    { key: "WIN", label: "Win Probability", weight: 0.15 },
    { key: "FIN", label: "Financial Value", weight: 0.15 },
    { key: "COMP", label: "Competitive Position", weight: 0.10 },
    { key: "FEAS", label: "Delivery Feasibility", weight: 0.10 },
    { key: "CUST", label: "Customer Relationship", weight: 0.10 },
    { key: "RISK", label: "Risk Exposure", weight: 0.10 },
    { key: "PROD", label: "Product / Service Compliance", weight: 0.05 },
    { key: "LEGAL", label: "Legal & Commercial Readiness", weight: 0.10 },
];

export const ScoreOpportunity: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const { user, authFetch } = useAuth();
    const [criteria, setCriteria] = useState<any[]>(DEFAULT_CRITERIA);

    const [opp, setOpp] = useState<any>(null);
    const [status, setStatus] = useState("NOT_STARTED");
    const [summary, setSummary] = useState("");
    const [confidence, setConfidence] = useState("MEDIUM");
    const [reco, setReco] = useState("PURSUE");
    const [currentVersion, setCurrentVersion] = useState<number | null>(null);
    const [prevAssessment, setPrevAssessment] = useState<any>(null);

    // Scoring State
    const [scores, setScores] = useState<Record<string, number>>({});
    const [selectedReasons, setSelectedReasons] = useState<Record<string, string[]>>({});
    const [sectionNotes, setSectionNotes] = useState<Record<string, string>>({});

    // Combined Review State
    const [combinedData, setCombinedData] = useState<any>(null);
    const isApprover = ['PH', 'GH', 'SH'].includes(user?.role || '');

    // State & Computed
    const [loading, setLoading] = useState(true);
    const [configError, setConfigError] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [attachmentName, setAttachmentName] = useState<string | null>(null);
    const [saSubmitted, setSaSubmitted] = useState(false);
    const [spSubmitted, setSpSubmitted] = useState(false);
    const [deadline, setDeadline] = useState("");

    const [lockedBy, setLockedBy] = useState<string | null>(null);
    const [lockedAt, setLockedAt] = useState<string | null>(null);

    const [dealValue, setDealValue] = useState<number>(0);
    const [patMargin, setPatMargin] = useState<number>(0);

    const isBM = user?.role === 'BM';
    const isSL = user?.role === 'SL';
    const isLocked = ['SUBMITTED', 'READY_FOR_REVIEW', 'APPROVED', 'REJECTED'].includes(status);
    const isDeadlinePassed = deadline ? new Date().getTime() > new Date(deadline).getTime() : false;
    
    // Lock logic: If locked by someone else, it's read-only
    const lockedBySomeoneElse = lockedBy && lockedBy !== user?.id;
    const isReadOnly = isLocked || !isBM || lockedBySomeoneElse;

    const weightedScore = criteria.reduce((acc, c) => acc + (scores[c.key] || 0) * (c.weight * 20), 0);

    useEffect(() => {
        const load = async () => {
            if (!id) return;
            const query = new URLSearchParams(location.search);
            const forcedVersion = query.get('version');

            try {
                // 1. Fetch Scoring Configuration (Task 2)
                try {
                    const configRes = await apiClient.get(API_ENDPOINTS.SCORING.CONFIG);
                    if (configRes.status === 200) {
                        const configData = configRes.data;
                        setCriteria(configData.map((d: any) => ({
                            key: d.section_code,
                            label: d.section_name,
                            weight: d.weight,
                            reasons: d.reasons || { critical: [], low: [], average: [], high: [], exceptional: [] }
                        })));
                    } else {
                        setConfigError("Failed to load scoring configuration");
                    }
                } catch (err) {
                    console.error("Config fetch error:", err);
                    setConfigError("Failed to load scoring configuration");
                }

                // 2. Fetch Opportunity Context
                const dRes = await apiClient.get(API_ENDPOINTS.INBOX.BY_ID(id));
                const dData = dRes.data;
                setOpp(dData);
                setDealValue(dData.deal_value || 0);
                setPatMargin(dData.pat_margin || 0);
                if (dData.close_date) {
                    setDeadline(new Date(dData.close_date).toISOString().split('T')[0]);
                }

                // 3. Fetch Assessment Data
                const isExecutor = isBM;
                const params: any = {};
                if (isExecutor && !forcedVersion) params.user_id = user?.id || '';
                if (forcedVersion) params.version = forcedVersion;

                const sRes = await apiClient.get(API_ENDPOINTS.SCORING.LATEST(id), { params });
                const sData = sRes.data;
                const currentStatus = sData.status;

                if (currentStatus !== "NOT_STARTED") {
                    setStatus(currentStatus);
                    setSaSubmitted(!!sData.sa_submitted);
                    setSpSubmitted(!!sData.sp_submitted);
                    setCurrentVersion(sData.version_no);
                    setPrevAssessment(sData.prev_assessment);
                    setSummary(sData.summary_comment || "");
                    setConfidence(sData.confidence_level || "MEDIUM");
                    setReco(sData.recommendation || "PURSUE");
                    setAttachmentName(sData.attachment_name || null);
                    setLockedBy(sData.locked_by || null);
                    setLockedAt(sData.locked_at || null);

                    const scoreMap: Record<string, number> = {};
                    const reasonMap: Record<string, string[]> = {};
                    const notesMap: Record<string, string> = {};

                    sData.sections.forEach((sec: any) => {
                        scoreMap[sec.section_code] = sec.score;
                        reasonMap[sec.section_code] = sec.selected_reasons || [];
                        notesMap[sec.section_code] = sec.notes || "";
                    });

                    setScores(scoreMap);
                    setSelectedReasons(reasonMap);
                    setSectionNotes(notesMap);

                    // 3b. If Ready for Review and User is Approver, Try Fetching Combined
                    const isReady = ['SUBMITTED', 'READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW'].includes(sData.status) ||
                        ['READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW'].includes(dData.workflow_status) ||
                        dData.combined_submission_ready;
                    if (isReady && isApprover) {
                        try {
                            const cParams = forcedVersion ? { version_no: forcedVersion } : {};
                            const cRes = await apiClient.get(API_ENDPOINTS.SCORING.COMBINED_REVIEW(id), { params: cParams });
                            setCombinedData(cRes.data);
                        } catch (e) { console.warn("Could not fetch combined data", e); }
                    }

                } else {
                    setCurrentVersion(sData.version_no || 1);
                    setPrevAssessment(sData.prev_assessment);
                    const initialScores: Record<string, number> = {};
                    criteria.forEach(c => initialScores[c.key] = 0.0);
                    setScores(initialScores);
                }

                // 4. Fetch History
                const hRes = await apiClient.get(API_ENDPOINTS.SCORING.HISTORY(id));
                setHistory(hRes.data);

            } catch (err) {
                console.error("Load Error", err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [id, isApprover, location.search, user?.id, user?.role]);

    const getVerdict = (score: number) => {
        if (score >= 80) return { label: 'Strong Pursue', class: 'verdict-strong' };
        if (score >= 60) return { label: 'Pursue', class: 'verdict-pursue' };
        if (score >= 40) return { label: 'Conditional', class: 'verdict-conditional' };
        return { label: 'Low Prospect', class: 'verdict-low' };
    };

    const verdict = getVerdict(weightedScore);

    const handleSave = async (isSubmit: boolean) => {
        if (isReadOnly) return;
        if (!user || !user.id) {
            alert("User session missing or invalid. Please re-login.");
            return;
        }
        if (isSubmit) {
            if (!summary || summary.trim().length < 20) {
                alert("A detailed Overall Justification Rationale (min 20 characters) is MANDATORY for submission.");
                return;
            }
            for (const c of criteria) {
                const score = scores[c.key] !== undefined ? scores[c.key] : 0.0;
                const reasons = selectedReasons[c.key] || [];
                const notes = sectionNotes[c.key] || "";
                if (score <= 2.0 || score >= 4.0) {
                    if (reasons.length < 1 && notes.trim().length < 10) {
                        alert(`For '${c.label}', a reason must be selected or a note (min 10 characters) provided because the score is high/low.`);
                        return;
                    }
                }
            }
        }

        setIsSaving(true);
        try {
            const payload = {
                user_id: user.id,
                sections: criteria.map(c => ({
                    section_code: c.key,
                    score: scores[c.key] !== undefined ? scores[c.key] : 0.0,
                    notes: sectionNotes[c.key] || "",
                    selected_reasons: selectedReasons[c.key] || []
                })),
                confidence_level: confidence,
                recommendation: reco,
                summary_comment: summary,
                attachment_name: attachmentName,
                financials: {
                    deal_value: dealValue,
                    pat_margin: patMargin
                }
            };

            const endpoint = isSubmit ? API_ENDPOINTS.SCORING.SUBMIT(id) : API_ENDPOINTS.SCORING.DRAFT(id);
            const res = await apiClient.post(endpoint, payload);

            if (res.status === 409) {
                const errorData = await res.json();
                alert(errorData.detail || "This assessment is currently being edited by another user.");
                // Update lock status locally to show warning
                return;
            }

            if (!res.ok) throw new Error("Submission failed");

            alert(isSubmit ? "Assessment Submitted Successfully!" : "Draft Saved.");
            navigate('/assigned-to-me');
        } catch (err: any) {
            alert("Submission Error:\n" + (err.response?.data?.detail || "Check connection."));
        } finally {
            setIsSaving(false);
        }
    };

    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
    const [approvalAction, setApprovalAction] = useState<'APPROVE' | 'REJECT' | null>(null);

    const openApprovalModal = (action: 'APPROVE' | 'REJECT') => {
        setApprovalAction(action);
        setIsApprovalModalOpen(true);
    };

    const handleModalConfirm = async (comment: string) => {
        if (!id || !approvalAction) return;
        setIsSaving(true);
        try {
            await apiClient.post(API_ENDPOINTS.OPPORTUNITIES.APPROVE(id || ''), {
                role: user?.role,
                decision: approvalAction,
                user_id: user?.id,
                comment: comment
            });
            alert(approvalAction === 'APPROVE' ? "Assessment Approved." : "Assessment Rejected.");
            navigate(user?.role === 'PH' ? '/practice-head/dashboard' : '/management/dashboard');
        } catch (err) {
            console.error(err);
            alert("Action failed.");
        } finally {
            setIsSaving(false);
            setIsApprovalModalOpen(false);
        }
    };

    const handleNewVersion = async () => {
        if (!confirm("Starting a new version will copy data from the latest version. Proceed?")) return;
        setIsSaving(true);
        try {
            await apiClient.post(API_ENDPOINTS.SCORING.NEW_VERSION(id || ''));
            alert("New Version Created.");
            window.location.reload();
        } catch (err) {
            alert("Failed to create new version.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleReopen = async () => {
        if (!confirm("Are you sure you want to re-open this assessment for editing?")) return;
        setIsSaving(true);
        try {
            await apiClient.post(API_ENDPOINTS.SCORING.REOPEN(id || ''));
            alert("Assessment re-opened as draft.");
            window.location.reload();
        } catch (err) {
            alert("Failed to re-open assessment.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append("file", file);
            try {
                const res = await apiClient.post(API_ENDPOINTS.UPLOAD, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                setAttachmentName(res.data.filename);
            } catch (err) {
                alert("Upload failed.");
            }
        }
    };

    const toggleReason = (key: string, reason: string) => {
        if (isReadOnly) return;
        const current = selectedReasons[key] || [];
        if (current.includes(reason)) {
            setSelectedReasons({ ...selectedReasons, [key]: current.filter(r => r !== reason) });
        } else {
            setSelectedReasons({ ...selectedReasons, [key]: [...current, reason] });
        }
    };

    if (loading) return <div className="p-loader">Retrieving Critical Data...</div>;
    if (configError) return <div className="p-loader text-red-500 bg-red-50 p-6 rounded-xl border border-red-200">{configError}</div>;
    if (!opp) return <div className="p-loader text-red-500">Opportunity Not Found</div>;

    const saAssessment = combinedData?.sa_assessment;
    const spAssessment = combinedData?.sp_assessment;

    return (
        <div className="assessment-root animate-fade">
            <header className="assessment-header">
                <div className="header-title-group">
                    <button className="back-btn-circle" onClick={() => navigate(-1)}><ArrowLeft size={20} /></button>
                    <div>
                        <h1 style={{ fontFamily: '"Libre Baskerville", serif', fontSize: '28px', color: '#333333' }} className="flex items-center gap-3">
                            {isApprover ? 'Review Assessment' : (isLocked ? 'View Finalized Assessment' : (currentVersion && currentVersion > 1 ? 'Update Assessment Version' : 'New Assessment'))}
                            {currentVersion && (
                                <span className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full text-xs font-black tracking-widest uppercase">
                                    <Hash size={12} /> Version {currentVersion}
                                </span>
                            )}
                        </h1>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    {isApprover && ['SUBMITTED', 'READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW'].includes(status) && (
                        <div className="flex gap-3">
                            <button onClick={() => openApprovalModal('REJECT')} className="px-6 py-2 bg-red-100 text-red-700 font-bold rounded-lg hover:bg-red-200 transition-colors">REJECT</button>
                            <button onClick={() => openApprovalModal('APPROVE')} className="px-6 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 shadow-md transition-all">APPROVE</button>
                        </div>
                    )}
                    {isBM && isLocked && !isDeadlinePassed && (
                        <div className="flex gap-2">
                            {status === 'SUBMITTED' && (
                                <button onClick={handleReopen} className="flex items-center gap-1 px-4 py-2 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-bold hover:bg-amber-100 shadow-sm">
                                    <RefreshCw size={14} /> Re-open Assessment
                                </button>
                            )}
                            <button onClick={handleNewVersion} className="flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 shadow-sm">
                                <RefreshCw size={14} /> Create New Version
                            </button>
                        </div>
                    )}
                </div>
            </header>

            <main className="main-assessment-content">
                <div className="assessment-form-area">
                    {isLocked && !isApprover && (
                        <div className="bg-amber-600 text-white px-6 py-2 font-black text-center text-xs tracking-[0.2em] uppercase mb-4 shadow-lg">
                            ⚠️ READ ONLY RECORD - Assessment Finalized
                        </div>
                    )}

                    {lockedBySomeoneElse && (
                        <div className="bg-red-600 text-white px-6 py-2 font-black text-center text-xs tracking-[0.2em] uppercase mb-4 shadow-lg animate-pulse">
                            ⚠️ CONCURRENCY LOCK - This assessment is currently being edited by another user
                        </div>
                    )}

                    {isApprover && combinedData && (
                        <div className="mx-8 mt-6 grid grid-cols-2 gap-6 scale-95 origin-top">
                            <div className={`p-6 rounded-2xl border-l-[6px] shadow-sm transition-all ${combinedData.sa_submitted ? 'bg-white border-blue-500' : 'bg-gray-50 border-gray-300 opacity-75'}`}>
                                <div className="flex justify-between items-start mb-2">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">Solution Architect Version</div>
                                    {combinedData.sa_submitted ? (
                                        <span className="flex items-center gap-1 text-[9px] font-black text-green-600 bg-green-50 px-2 py-0.5 rounded-full uppercase">Submitted</span>
                                    ) : (
                                        <span className="flex items-center gap-1 text-[9px] font-black text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full uppercase italic">Pending Submission</span>
                                    )}
                                </div>
                                {combinedData.sa_submitted ? (
                                    <>
                                        <div className="text-3xl font-black text-gray-900">{combinedData.sa_assessment?.score?.toFixed(1) || '0.0'}%</div>
                                        <div className="text-xs text-gray-500 mt-2 font-medium italic">Validated by: {combinedData.sa_info?.name || 'Assigned SA'}</div>
                                    </>
                                ) : (
                                    <div className="py-4 text-sm font-bold text-gray-400 italic">
                                        SA Version not yet present in this assessment round.
                                        <p className="text-[10px] mt-1 font-medium normal-case">Assigned to: {combinedData.sa_info?.name}</p>
                                    </div>
                                )}
                            </div>

                            <div className={`p-6 rounded-2xl border-l-[6px] shadow-sm transition-all ${combinedData.sp_submitted ? 'bg-white border-purple-500' : 'bg-gray-50 border-gray-300 opacity-75'}`}>
                                <div className="flex justify-between items-start mb-2">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">Sales Person Version</div>
                                    {combinedData.sp_submitted ? (
                                        <span className="flex items-center gap-1 text-[9px] font-black text-green-600 bg-green-50 px-2 py-0.5 rounded-full uppercase">Submitted</span>
                                    ) : (
                                        <span className="flex items-center gap-1 text-[9px] font-black text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full uppercase italic">Pending Submission</span>
                                    )}
                                </div>
                                {combinedData.sp_submitted ? (
                                    <>
                                        <div className="text-3xl font-black text-gray-900">{combinedData.sp_assessment?.score?.toFixed(1) || '0.0'}%</div>
                                        <div className="text-xs text-gray-500 mt-2 font-medium italic">Validated by: {combinedData.sp_info?.name || 'Assigned SP'}</div>
                                    </>
                                ) : (
                                    <div className="py-4 text-sm font-bold text-gray-400 italic">
                                        SP Version not yet present in this assessment round.
                                        <p className="text-[10px] mt-1 font-medium normal-case">Assigned to: {combinedData.sp_info?.name}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    <div className="assessment-card" style={{ borderLeft: '4px solid #0073BB' }}>
                        <h3 className="text-[11px] font-black uppercase tracking-widest text-[#666666] mb-6">Oracle Opportunity Context</h3>
                        <div className="context-grid grid grid-cols-3 gap-8">
                            <div className="context-item">
                                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-1">Account</label>
                                <div className="text-lg font-bold text-gray-900">{opp.customer_name || '-'}</div>
                            </div>
                            <div className="context-item">
                                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-1">Revenue (USD)</label>
                                {!isReadOnly ? (
                                    <input 
                                        type="number" 
                                        value={dealValue} 
                                        onChange={(e) => setDealValue(parseFloat(e.target.value))}
                                        className="text-lg font-bold text-green-600 bg-transparent border-b border-green-200 outline-none focus:border-green-500 w-full"
                                    />
                                ) : (
                                    <div className="text-lg font-bold text-green-600">${dealValue?.toLocaleString() || '0'}</div>
                                )}
                            </div>
                            <div className="context-item">
                                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-1">PAT Margin (%)</label>
                                {!isReadOnly ? (
                                    <input 
                                        type="number" 
                                        step="0.1"
                                        value={patMargin} 
                                        onChange={(e) => setPatMargin(parseFloat(e.target.value))}
                                        className="text-lg font-bold text-purple-600 bg-transparent border-b border-purple-200 outline-none focus:border-purple-500 w-full"
                                    />
                                ) : (
                                    <div className="text-lg font-bold text-purple-600">{patMargin || 0}%</div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="section-divider mb-8 mt-12 px-6 bg-blue-50/50 p-8 rounded-3xl border border-blue-100">
                        <h2 className="text-xl font-black text-gray-900 mb-2">Bid Quality Assessment Framework</h2>
                        <p className="text-gray-600 leading-relaxed max-w-2xl">
                            Evaluate this opportunity using the 9-factor methodology. Scores are weighted by critical impact.
                            <b> 1.0 = Risk/Blocker, 3.0 = Standard Alignment, 5.0 = Competitive Advantage.</b>
                            Please provide specific commentary for any scores below 2.0 or above 4.0.
                        </p>
                    </div>

                    <div className="scoring-grid space-y-8 px-6 pb-12">
                        {criteria.map((c) => {
                            const currentScore = scores[c.key] !== undefined ? scores[c.key] : 0.0;
                            const options = c.reasons || { critical: [], low: [], average: [], high: [], exceptional: [] };

                            let reasonPool = options.average;
                            if (currentScore >= 4.5) reasonPool = options.exceptional;
                            else if (currentScore >= 3.5) reasonPool = options.high;
                            else if (currentScore >= 2.5) reasonPool = options.average;
                            else if (currentScore >= 1.5) reasonPool = options.low;
                            else reasonPool = options.critical;

                            const saSec = saAssessment?.sections?.find((s: any) => s.code === c.key);
                            const spSec = spAssessment?.sections?.find((s: any) => s.code === c.key);

                            return (
                                <div key={c.key} className="eval-card bg-white p-8 rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl transition-all">
                                    <div className="eval-header flex justify-between items-start mb-8">
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-900 mb-1">{c.label}</h3>
                                            <p className="text-xs text-gray-400 font-medium">Weight: {(c.weight * 100).toFixed(0)}%</p>
                                        </div>
                                        <div className="flex flex-col items-end gap-2">
                                            <div className="score-display text-3xl font-black text-blue-600 bg-blue-50 px-4 py-2 rounded-xl">
                                                {currentScore.toFixed(1)}
                                            </div>
                                            {isApprover && combinedData && (
                                                <div className="flex flex-col items-end gap-1.5">
                                                    <div className="flex gap-2">
                                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter ${combinedData.sa_submitted ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-400'}`}>
                                                            SA: {combinedData.sa_submitted ? (saSec?.score?.toFixed(1) || '0.0') : 'N/P'}
                                                        </span>
                                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter ${combinedData.sp_submitted ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'}`}>
                                                            SP: {combinedData.sp_submitted ? (spSec?.score?.toFixed(1) || '0.0') : 'N/P'}
                                                        </span>
                                                    </div>
                                                    {(!combinedData.sa_submitted || !combinedData.sp_submitted) && (
                                                        <div className="text-[8px] font-bold text-amber-500 uppercase tracking-widest italic animate-pulse">
                                                            {(!combinedData.sa_submitted && !combinedData.sp_submitted) ? 'BOTH VERSIONS PENDING' : (!combinedData.sa_submitted ? 'SA VERSION NOT PRESENT' : 'SP VERSION NOT PRESENT')}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div className="relative mb-8 pt-2">
                                        <input
                                            type="range"
                                            min="0" max="5" step="0.5"
                                            disabled={isReadOnly}
                                            value={currentScore}
                                            onChange={(e) => setScores({ ...scores, [c.key]: parseFloat(e.target.value) })}
                                            className="w-full h-2 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-blue-600 block"
                                        />
                                        <div className="flex justify-between mt-4 px-1">
                                            {[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5].map(v => (
                                                <div key={v} className="flex flex-col items-center gap-1">
                                                    <div className={`w-0.5 h-2 ${v % 1 === 0 ? 'bg-gray-400' : 'bg-gray-200'}`}></div>
                                                    <span className={`text-[10px] font-bold ${v === currentScore ? 'text-blue-600 scale-125' : 'text-gray-400'}`}>
                                                        {v.toFixed(1)}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                        <div>
                                            <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 block mb-4">Drivers & Rationales</label>
                                            <div className="grid grid-cols-1 gap-2">
                                                {(reasonPool || []).map((r: string) => (
                                                    <label
                                                        key={r}
                                                        className={`flex items-center gap-3 p-3 rounded-xl border text-xs font-semibold cursor-pointer transition-all ${(selectedReasons[c.key] || []).includes(r)
                                                            ? 'bg-blue-600 border-blue-600 text-white shadow-md'
                                                            : 'bg-gray-50 border-gray-100 text-gray-600 hover:border-blue-200'
                                                            }`}
                                                        onClick={() => toggleReason(c.key, r)}
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            checked={(selectedReasons[c.key] || []).includes(r)}
                                                            readOnly
                                                            className="hidden"
                                                        />
                                                        {r}
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 block mb-4">Custom Drivers & Observations</label>
                                            <textarea
                                                className="w-full h-[150px] p-4 bg-gray-50 border border-gray-100 rounded-2xl text-sm italic outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                                                placeholder={`Document specific observations for ${c.label} if not covered by presets...`}
                                                value={sectionNotes[c.key] || ""}
                                                disabled={isReadOnly}
                                                onChange={(e) => setSectionNotes({ ...sectionNotes, [c.key]: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Assessment & Governance History Log */}
                    {history.length > 0 && (
                        <div className="mx-8 mt-12 mb-8 bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                            <div className="px-8 py-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                                <div>
                                    <h3 className="text-lg font-black text-gray-900 leading-none">Assessment & Governance History</h3>
                                    <p className="text-xs text-gray-500 mt-2">Audit trail of all versions, decisions, and rationales</p>
                                </div>
                                <RefreshCw size={18} className="text-gray-300" />
                            </div>
                            <div className="divide-y divide-gray-50">
                                {history.map((h, idx) => (
                                    <div key={idx} className="px-8 py-6 hover:bg-gray-50/50 transition-colors">
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="flex items-center gap-4">
                                                <div className="flex flex-col items-center justify-center w-12 h-12 bg-blue-50 rounded-xl border border-blue-100">
                                                    <span className="text-[10px] font-black text-blue-400 uppercase leading-none">Ver</span>
                                                    <span className="text-xl font-black text-blue-600 leading-none mt-1">{h.version}</span>
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-3">
                                                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest ${h.status === 'APPROVED' ? 'bg-green-100 text-green-700' :
                                                            h.status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                                                                'bg-blue-100 text-blue-700'
                                                            }`}>
                                                            {h.status}
                                                        </span>
                                                        <span className="text-sm font-bold text-gray-900">{h.score}% Score</span>
                                                    </div>
                                                    <p className="text-xs text-gray-400 mt-1 font-medium">
                                                        By {h.created_by} • {new Date(h.created_at).toLocaleString()}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-[10px] font-black uppercase text-gray-400 tracking-widest leading-none">Recommendation</div>
                                                <div className="text-sm font-bold text-gray-900 mt-1">{h.recommendation}</div>
                                            </div>
                                        </div>
                                        <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
                                            <div className="text-[9px] font-black uppercase text-gray-400 tracking-widest mb-1.5">Rationale & Governance Notes</div>
                                            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap italic">
                                                {h.summary || "No rationale provided."}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="summary-dark bg-gray-900 text-white p-12 mt-12 rounded-t-[3rem]">
                        <div className="grid grid-cols-2 gap-12 mb-12">
                            <div>
                                <label className="text-gray-400 font-bold uppercase tracking-widest text-xs">Weighted Score</label>
                                <div className="text-6xl font-black mt-2 text-blue-400">{weightedScore.toFixed(2)}</div>
                            </div>
                            <div>
                                <label className="text-gray-400 font-bold uppercase tracking-widest text-xs">Verdict</label>
                                <div className={`text-4xl font-black mt-2 ${verdict.class}`}>{verdict.label}</div>
                            </div>
                        </div>

                        {/* Attachment Section */}
                        <div className="mb-12">
                            <label className="block text-gray-400 font-bold uppercase tracking-widest text-xs mb-4">Supporting Evidence / Attachments</label>
                            <div className="flex flex-wrap gap-4">
                                {isBM && !attachmentName && !isReadOnly ? (
                                    <div className="flex-1">
                                        <label className="attachment-section group">
                                            <input type="file" className="hidden" onChange={handleFileUpload} disabled={isReadOnly} />
                                            <div className="flex flex-col items-center gap-2">
                                                <Upload className="text-gray-400 group-hover:text-blue-500 transition-colors" size={32} />
                                                <div className="text-sm font-bold text-gray-500 group-hover:text-gray-700">Click to Upload Relevant Docs</div>
                                                <div className="text-[10px] text-gray-400 uppercase tracking-widest font-black">PDF, PNG, JPG, XLSX (Max 10MB)</div>
                                            </div>
                                        </label>
                                    </div>
                                ) : (
                                    attachmentName && (
                                        <div className="file-pill">
                                            <FileText size={16} className="text-blue-600" />
                                            <span className="truncate max-w-[200px]">{attachmentName}</span>
                                            {!isReadOnly && (
                                                <button onClick={() => setAttachmentName(null)} className="trash-btn">
                                                    <Trash2 size={14} />
                                                </button>
                                            )}
                                        </div>
                                    )
                                )}
                            </div>
                        </div>

                        <div className="mb-12">
                            <label className="block text-gray-400 font-bold uppercase tracking-widest text-xs mb-4">Overall Justification Rationale (Mandatory)</label>
                            <textarea
                                className="w-full h-48 bg-white/5 border border-white/10 rounded-3xl p-8 text-white text-lg placeholder:text-white/20 outline-none focus:border-blue-500 transition-all"
                                placeholder="Explain the strategic reasoning for this score..."
                                value={summary}
                                disabled={isReadOnly}
                                onChange={(e) => setSummary(e.target.value)}
                            />
                        </div>

                        <div className="flex items-center justify-between pt-12 border-t border-white/10">
                            <button className="px-8 py-4 text-white hover:text-blue-400 font-bold transition-all" onClick={() => navigate(-1)}>Back</button>
                            <div className="flex gap-6">
                                {!isReadOnly && (
                                    <>
                                        <button className="px-10 py-4 bg-white/5 border border-white/10 rounded-2xl font-bold hover:bg-white/10" onClick={() => handleSave(false)}>Save Draft</button>
                                        <button className="px-10 py-4 bg-blue-600 rounded-2xl font-black hover:bg-blue-700 shadow-xl" onClick={() => handleSave(true)}>Submit Assessment</button>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Sidebar removed as per requirement */}
            </main>

            <ApprovalModal
                isOpen={isApprovalModalOpen}
                onClose={() => setIsApprovalModalOpen(false)}
                onConfirm={handleModalConfirm}
                type={approvalAction || 'APPROVE'}
            />
        </div>
    );
};
