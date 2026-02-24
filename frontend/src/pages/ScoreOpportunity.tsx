
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { REASON_OPTIONS, CRITERIA_WEIGHTS } from '../constants/scoringCriteria';
import { ArrowLeft, Save, Send, AlertTriangle, FileText, Upload, Trash2, CheckCircle, Edit3, RefreshCw, Hash } from 'lucide-react';
import { ApprovalModal } from '../components/ApprovalModal';
import '../styles/Assessment.css';

const CRITERIA = [
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
    const { user } = useAuth();

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
    const [isSaving, setIsSaving] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [attachmentName, setAttachmentName] = useState<string | null>(null);
    const [saSubmitted, setSaSubmitted] = useState(false);
    const [spSubmitted, setSpSubmitted] = useState(false);
    const [deadline, setDeadline] = useState("");

    const isSA = user?.role === 'SA';
    const isSP = user?.role === 'SP';
    const isLocked = ['SUBMITTED', 'READY_FOR_REVIEW', 'APPROVED', 'REJECTED'].includes(status);
    const isDeadlinePassed = deadline ? new Date().getTime() > new Date(deadline).getTime() : false;
    const isUserSubmitted = (isSA && saSubmitted) || (isSP && spSubmitted);
    const isReadOnly = isLocked || isUserSubmitted || (!isSA && !isSP);

    const weightedScore = CRITERIA.reduce((acc, c) => acc + (scores[c.key] || 0) * (c.weight * 20), 0);

    useEffect(() => {
        const load = async () => {
            if (!id) return;
            const query = new URLSearchParams(location.search);
            const forcedVersion = query.get('version');

            try {
                // 1. Fetch Opportunity Context
                const d = await axios.get(`http://localhost:8000/api/inbox/${id}`);
                setOpp(d.data);
                if (d.data.close_date) {
                    setDeadline(new Date(d.data.close_date).toISOString().split('T')[0]);
                }

                // 2. Fetch Assessment Data
                const isExecutor = user?.role === 'SA' || user?.role === 'SP';
                const params = new URLSearchParams();
                if (isExecutor && !forcedVersion) params.append('user_id', user?.id || '');
                if (forcedVersion) params.append('version', forcedVersion);

                const s = await axios.get(`http://localhost:8000/api/scoring/${id}/latest?${params.toString()}`);
                const currentStatus = s.data.status;

                if (currentStatus !== "NOT_STARTED") {
                    setStatus(currentStatus);
                    setSaSubmitted(!!s.data.sa_submitted);
                    setSpSubmitted(!!s.data.sp_submitted);
                    setCurrentVersion(s.data.version_no);
                    setPrevAssessment(s.data.prev_assessment);
                    setSummary(s.data.summary_comment || "");
                    setConfidence(s.data.confidence_level || "MEDIUM");
                    setReco(s.data.recommendation || "PURSUE");
                    setAttachmentName(s.data.attachment_name || null);

                    const scoreMap: Record<string, number> = {};
                    const reasonMap: Record<string, string[]> = {};
                    const notesMap: Record<string, string> = {};

                    s.data.sections.forEach((sec: any) => {
                        scoreMap[sec.section_code] = sec.score;
                        reasonMap[sec.section_code] = sec.selected_reasons || [];
                        notesMap[sec.section_code] = sec.notes || "";
                    });

                    setScores(scoreMap);
                    setSelectedReasons(reasonMap);
                    setSectionNotes(notesMap);

                    // 2b. If Ready for Review and User is Approver, Try Fetching Combined
                    const isReady = ['SUBMITTED', 'READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW'].includes(s.data.status) ||
                        ['READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW'].includes(d.data.workflow_status) ||
                        d.data.combined_submission_ready;
                    if (isReady && isApprover) {
                        try {
                            const cParams = forcedVersion ? `?version_no=${forcedVersion}` : '';
                            const c = await axios.get(`http://localhost:8000/api/scoring/${id}/combined-review${cParams}`);
                            setCombinedData(c.data);
                        } catch (e) { console.warn("Could not fetch combined data", e); }
                    }

                } else {
                    setCurrentVersion(s.data.version_no || 1);
                    setPrevAssessment(s.data.prev_assessment);
                    const initialScores: Record<string, number> = {};
                    CRITERIA.forEach(c => initialScores[c.key] = 0.0);
                    setScores(initialScores);
                }

                // 3. Fetch History
                const h = await axios.get(`http://localhost:8000/api/scoring/${id}/history`);
                setHistory(h.data);

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
            for (const c of CRITERIA) {
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
                sections: CRITERIA.map(c => ({
                    section_code: c.key,
                    score: scores[c.key] !== undefined ? scores[c.key] : 0.0,
                    notes: sectionNotes[c.key] || "",
                    selected_reasons: selectedReasons[c.key] || []
                })),
                confidence_level: confidence,
                recommendation: reco,
                summary_comment: summary,
                attachment_name: attachmentName
            };

            const endpoint = isSubmit ? 'submit' : 'draft';
            await axios.post(`http://localhost:8000/api/scoring/${id}/${endpoint}`, payload);

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
            await axios.post(`http://localhost:8000/api/opportunities/${id}/approve`, {
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
            await axios.post(`http://localhost:8000/api/scoring/${id}/new-version`);
            alert("New Version Created.");
            window.location.reload();
        } catch (err) {
            alert("Failed to create new version.");
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
                const res = await axios.post('http://localhost:8000/api/upload', formData);
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
                    {(isSA || isSP) && isLocked && !isDeadlinePassed && (
                        <button onClick={handleNewVersion} className="flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 shadow-sm">
                            <RefreshCw size={14} /> Create New Version
                        </button>
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
                                <div className="text-lg font-bold text-green-600">${opp.deal_value?.toLocaleString() || '0'}</div>
                            </div>
                            <div className="context-item">
                                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-1">Current Status</label>
                                <div className="text-lg font-bold text-blue-600">{(opp.workflow_status || 'NEW').replace(/_/g, ' ')}</div>
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
                        {CRITERIA.map((c) => {
                            const currentScore = scores[c.key] !== undefined ? scores[c.key] : 0.0;
                            const options = REASON_OPTIONS[c.key] || { critical: [], low: [], average: [], high: [], exceptional: [] };

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
                                                            SA: {combinedData.sa_submitted ? (saSec?.score || '0.0') : 'N/P'}
                                                        </span>
                                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter ${combinedData.sp_submitted ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'}`}>
                                                            SP: {combinedData.sp_submitted ? (spSec?.score || '0.0') : 'N/P'}
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
                                                {reasonPool.map(r => (
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
                                {!attachmentName ? (
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
                                    <div className="file-pill">
                                        <FileText size={16} className="text-blue-600" />
                                        <span className="truncate max-w-[200px]">{attachmentName}</span>
                                        {!isReadOnly && (
                                            <button onClick={() => setAttachmentName(null)} className="trash-btn">
                                                <Trash2 size={14} />
                                            </button>
                                        )}
                                    </div>
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
