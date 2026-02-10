
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { REASON_OPTIONS, CRITERIA_WEIGHTS } from '../constants/scoringCriteria';
import { ArrowLeft, Save, Send, AlertTriangle, FileText, Upload, Trash2, CheckCircle, Edit3, RefreshCw } from 'lucide-react';
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

    // Core States
    const [opp, setOpp] = useState<any>(null);
    const [status, setStatus] = useState("NOT_STARTED");
    const [currentVersion, setCurrentVersion] = useState<number | null>(null);
    const [prevAssessment, setPrevAssessment] = useState<any>(null);
    const [scores, setScores] = useState<Record<string, number>>({});
    const [selectedReasons, setSelectedReasons] = useState<Record<string, string[]>>({});
    const [sectionNotes, setSectionNotes] = useState<Record<string, string>>({});
    const [summary, setSummary] = useState("");
    const [confidence, setConfidence] = useState("MEDIUM");
    // Combined Review State
    const [combinedData, setCombinedData] = useState<any>(null);
    const isApprover = ['PH', 'GH', 'SH'].includes(user?.role || '');

    // State & Computed
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const [reco, setReco] = useState("PURSUE");
    const [attachmentName, setAttachmentName] = useState<string | null>(null);
    const [saSubmitted, setSaSubmitted] = useState(false);
    const [spSubmitted, setSpSubmitted] = useState(false);
    const [isIdentityEditable, setIsIdentityEditable] = useState(false);
    const [deadline, setDeadline] = useState("");

    const isSA = user?.role === 'SA';
    const isSP = user?.role === 'SP';
    const isLocked = ['SUBMITTED', 'READY_FOR_REVIEW', 'APPROVED', 'REJECTED'].includes(status);
    const isDeadlinePassed = deadline ? new Date().getTime() > new Date(deadline).getTime() : false;
    const isUserSubmitted = (isSA && saSubmitted) || (isSP && spSubmitted);
    const isReadOnly = isLocked || isUserSubmitted || (isApprover && status !== 'NOT_STARTED' && status !== 'DRAFT');

    useEffect(() => {
        const load = async () => {
            if (!id) return;
            const query = new URLSearchParams(location.search);
            const forcedVersion = query.get('version');

            try {
                // 1. Fetch Opportunity Context
                const d = await axios.get(`http://127.0.0.1:8000/api/inbox/${id}`);
                setOpp(d.data);
                if (d.data.close_date) {
                    setDeadline(new Date(d.data.close_date).toISOString().split('T')[0]);
                }

                // 2. Fetch Assessment Data
                const isExecutor = user?.role === 'SA' || user?.role === 'SP';
                const params = new URLSearchParams();
                if (isExecutor && !forcedVersion) params.append('user_id', user?.id || '');
                if (forcedVersion) params.append('version', forcedVersion);

                const s = await axios.get(`http://127.0.0.1:8000/api/scoring/${id}/latest?${params.toString()}`);
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
                            const c = await axios.get(`http://127.0.0.1:8000/api/scoring/${id}/combined-review${cParams}`);
                            setCombinedData(c.data);
                        } catch (e) { console.warn("Could not fetch combined data", e); }
                    }

                } else {
                    // Initialize with 3.0
                    setCurrentVersion(s.data.version_no || 1);
                    setPrevAssessment(s.data.prev_assessment);
                    const initialScores: Record<string, number> = {};
                    CRITERIA.forEach(c => initialScores[c.key] = 3.0);
                    setScores(initialScores);
                    setIsIdentityEditable(true); // Default to editable for new assessments
                }

                // 3. Fetch History
                const h = await axios.get(`http://127.0.0.1:8000/api/scoring/${id}/history`);
                setHistory(h.data);

            } catch (err) {
                console.error("Load Error", err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [id, isApprover, location.search]);

    const calculateWeightedScore = () => {
        let total = 0;
        CRITERIA.forEach(c => {
            total += (scores[c.key] || 3.0) * c.weight;
        });
        return parseFloat(total.toFixed(2));
    };

    const weightedScore = calculateWeightedScore();

    const getVerdict = (score: number) => {
        if (score >= 4.0) return { label: "PURSUE AGGRESSIVELY", class: "go" };
        if (score >= 3.5) return { label: "PURSUE WITH GEO-HEAD APPROVAL", class: "review" };
        return { label: "NO GO / REVIEW", class: "nogo" };
    };

    const verdict = getVerdict(weightedScore);

    const handleSave = async (isSubmit: boolean) => {
        if (!user || !user.id) {
            alert("User session missing or invalid. Please re-login.");
            return;
        }
        if (isSubmit) {
            if (!summary || summary.trim().length < 20) {
                alert("A detailed Overall Justification Rationale (min 20 characters) is MANDATORY for submission.");
                return;
            }

            // Check section rationales for deviant scores
            for (const c of CRITERIA) {
                const score = scores[c.key] || 3.0;
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
                    score: scores[c.key] || 3.0,
                    notes: sectionNotes[c.key] || "",
                    selected_reasons: selectedReasons[c.key] || []
                })),
                confidence_level: confidence,
                recommendation: reco,
                summary_comment: summary,
                attachment_name: attachmentName
            };

            const endpoint = isSubmit ? 'submit' : 'draft';
            await axios.post(`http://127.0.0.1:8000/api/scoring/${id}/${endpoint}`, payload);

            alert(isSubmit ? "Assessment Submitted Successfully!" : "Draft Saved.");
            navigate('/assigned-to-me');
        } catch (err: any) {
            const errorData = err.response?.data?.detail;
            const message = Array.isArray(errorData)
                ? errorData.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
                : (typeof errorData === 'string' ? errorData : "Check connection.");

            alert("Submission Error:\n" + message);
        } finally {
            setIsSaving(false);
        }
    };


    // --- Approval Modal Logic ---
    const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
    const [approvalAction, setApprovalAction] = useState<'APPROVE' | 'REJECT' | null>(null);

    const openApprovalModal = (action: 'APPROVE' | 'REJECT') => {
        if (!id) return;
        setApprovalAction(action);
        setIsApprovalModalOpen(true);
    };

    const handleModalConfirm = async (comment: string) => {
        if (!id || !approvalAction) return;

        setIsSaving(true);
        try {
            await axios.post(`http://127.0.0.1:8000/api/opportunities/${id}/approve`, {
                role: user?.role,
                decision: approvalAction,
                user_id: user?.id,
                comment: comment
            });
            alert(approvalAction === 'APPROVE' ? "Assessment Approved." : "Assessment Rejected.");
            navigate(user?.role === 'PH' ? '/practice-head' : '/dashboard');
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
            await axios.post(`http://127.0.0.1:8000/api/scoring/${id}/new-version`);
            alert("New Version Created.");
            window.location.reload();
        } catch (err) {
            alert("Failed to create new version.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleReopen = async () => {
        if (!window.confirm("Are you sure you want to re-open this assessment for editing?")) return;
        setIsSaving(true);
        try {
            await axios.post(`http://127.0.0.1:8000/api/scoring/${id}/reopen`);
            alert("Assessment re-opened. You can now edit and save as draft.");
            window.location.reload();
        } catch (err: any) {
            alert("Error: " + (err.response?.data?.detail || "Could not re-open."));
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
                const res = await axios.post('http://127.0.0.1:8000/api/upload', formData);
                setAttachmentName(res.data.filename);
            } catch (err) {
                alert("Upload failed.");
            }
        }
    };

    if (loading) return <div className="p-loader">Retrieving Critical Data...</div>;
    if (!opp) return <div className="p-loader text-red-500">Opportunity Not Found</div>;

    // --- Combined View Renderer ---
    if (combinedData && isApprover) {
        return (
            <div className="p-8 bg-gray-50 min-h-screen">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center gap-4 mb-8">
                        <button className="p-2 rounded-full bg-white border border-gray-200 hover:bg-gray-50" onClick={() => navigate(-1)}><ArrowLeft size={20} /></button>
                        <div className="flex-1">
                            <h1 className="text-2xl font-bold text-gray-900">Combined Assessment Review</h1>
                            <p className="text-gray-500">Comparing Solution Architect vs Sales Person assessments</p>
                        </div>

                        {/* Approval Matrix */}
                        <div className="flex items-center gap-2 mr-6 text-xs font-semibold bg-white p-2 rounded-lg border border-gray-100 shadow-sm">
                            <div className={`px-2 py-1 rounded ${combinedData.approvals?.ph === 'APPROVED' ? 'bg-green-100 text-green-700' : combinedData.approvals?.ph === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                                PH: {combinedData.approvals?.ph || 'PENDING'}
                            </div>
                            <div className={`px-2 py-1 rounded ${combinedData.approvals?.sh === 'APPROVED' ? 'bg-green-100 text-green-700' : combinedData.approvals?.sh === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                                SH: {combinedData.approvals?.sh || 'PENDING'}
                            </div>
                            <div className={`px-2 py-1 rounded ${combinedData.approvals?.gh === 'APPROVED' ? 'bg-green-100 text-green-700' : combinedData.approvals?.gh === 'REJECTED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'}`}>
                                GH: {combinedData.approvals?.gh || 'PENDING'}
                            </div>
                        </div>

                        {/* Action Buttons: Show if Current User has NOT voted yet */}
                        <div className="flex gap-3">
                            {(() => {
                                const myRole = user?.role?.toLowerCase();
                                const myStatus = combinedData.approvals?.[myRole];
                                const isMyTurn = myStatus === 'PENDING' || myStatus === 'NOTIFIED';

                                if (isMyTurn) {
                                    return (
                                        <>
                                            <button onClick={() => openApprovalModal('REJECT')} className="px-6 py-2 bg-red-100 text-red-700 font-bold rounded hover:bg-red-200">REJECT</button>
                                            <button onClick={() => openApprovalModal('APPROVE')} className="px-6 py-2 bg-green-600 text-white font-bold rounded hover:bg-green-700 shadow-md">APPROVE</button>
                                        </>
                                    );
                                } else {
                                    return <div className="px-4 py-2 bg-gray-100 text-gray-500 font-bold rounded">You have {myStatus?.toLowerCase()}</div>;
                                }
                            })()}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-8">
                        {/* SA Column */}
                        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-blue-500">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-lg font-bold text-gray-800">Solution Architect</h2>
                                <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                    {combinedData?.sa_assessment?.created_by || 'Technical Assessment'}
                                </span>
                            </div>
                            <div className="text-4xl font-black text-gray-900 mb-2">{combinedData?.sa_assessment?.score || 0}%</div>
                            <p className="text-sm text-gray-600 italic mb-6">Recommendation: {combinedData?.sa_assessment?.recommendation || 'N/A'}</p>

                            <div className="space-y-4">
                                {combinedData.sa_score?.sections.map((s: any) => (
                                    <div key={s.section_code} className="flex justify-between border-b border-gray-100 pb-2">
                                        <span className="text-sm text-gray-600">{s.section_code}</span>
                                        <span className="font-bold">{s.score}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* SP Column */}
                        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-purple-500">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-lg font-bold text-gray-800">Sales Person</h2>
                                <span className="text-xs font-bold bg-purple-100 text-purple-700 px-2 py-1 rounded">
                                    {combinedData?.sp_assessment?.created_by || 'Commercial Assessment'}
                                </span>
                            </div>
                            <div className="text-4xl font-black text-gray-900 mb-2">{combinedData?.sp_assessment?.score || 0}%</div>
                            <p className="text-sm text-gray-600 italic mb-6">Recommendation: {combinedData?.sp_assessment?.recommendation || 'N/A'}</p>

                            <div className="space-y-4">
                                {combinedData.sp_score?.sections?.map((s: any) => (
                                    <div key={s.section_code} className="flex justify-between border-b border-gray-100 pb-2">
                                        <span className="text-sm text-gray-600">{s.section_code}</span>
                                        <span className="font-bold">{s.score}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // --- Standard View (Single Assessment) ---
    return (
        <div className="assessment-root animate-fade">
            <header className="assessment-header">
                <div className="header-title-group">
                    <button className="back-btn-circle" onClick={() => navigate(-1)}><ArrowLeft size={20} /></button>
                    <div>
                        <h1 style={{ fontFamily: '"Libre Baskerville", serif', fontSize: '28px', color: '#333333' }}>
                            {isLocked ? 'View Finalized Assessment' : (currentVersion && currentVersion > 1 ? 'Update Assessment Version' : 'New Assessment')}
                        </h1>
                        <p className="header-subtitle" style={{ color: '#666666', fontWeight: 500 }}>Bid Qualification and Scoring Form</p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    {/* ... (Existing Header Buttons) ... */}
                    {(isSA || isSP) && isLocked && !isDeadlinePassed && (
                        <button
                            onClick={handleNewVersion}
                            className="flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 transition-all shadow-sm"
                        >
                            <RefreshCw size={14} className="animate-spin-slow" /> Create New Version
                        </button>
                    )}
                    {/* ... */}
                </div>
            </header>

            {/* Read-Only Status Banner */}
            {isLocked && (
                <div className="bg-amber-600 text-white px-6 py-2 font-black text-center text-xs tracking-[0.2em] uppercase mb-4 rounded shadow-lg animate-pulse">
                    ⚠️ READ ONLY RECORD - Assessment Finalized
                </div>
            )}

            {/* Re-Assessment Cycle Banner */}
            {!isLocked && currentVersion && currentVersion > 1 && (
                <div className="bg-blue-600 text-white px-6 py-4 rounded-xl shadow-lg border-2 border-blue-400 mb-6 flex items-center justify-between animate-fade-in">
                    <div className="flex items-center gap-4">
                        <div className="bg-white/20 p-2 rounded-full"><RefreshCw size={24} className="animate-spin-slow" /></div>
                        <div>
                            <div className="font-black text-xs uppercase tracking-widest opacity-80">Cycle Clarity</div>
                            <div className="text-lg font-bold">Re-Assessment Active: Version {currentVersion}</div>
                            <p className="text-sm opacity-90">Previously assessed values have been cloned for your reference.</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Dual Submission Tracking Banner */}
            {!isLocked && (saSubmitted || spSubmitted) && (
                <div className="bg-indigo-600 text-white px-6 py-3 rounded-xl shadow-lg mb-6 flex items-center justify-between animate-fade-in">
                    <div className="flex items-center gap-8">
                        <div className="flex items-center gap-2">
                            <CheckCircle size={18} className={saSubmitted ? "text-green-400" : "text-white/30"} />
                            <span className="text-xs font-bold uppercase tracking-wider">Solution Architect: {saSubmitted ? "SUBMITTED" : "PENDING"}</span>
                        </div>
                        <div className="divider-v h-4 w-[1px] bg-white/20"></div>
                        <div className="flex items-center gap-2">
                            <CheckCircle size={18} className={spSubmitted ? "text-green-400" : "text-white/30"} />
                            <span className="text-xs font-bold uppercase tracking-wider">Sales Person: {spSubmitted ? "SUBMITTED" : "PENDING"}</span>
                        </div>
                    </div>
                    {isUserSubmitted && <span className="text-[10px] bg-white/40 px-3 py-1 rounded-full font-black tracking-tighter blink">LOCKED: YOUR PART SUBMITTED</span>}
                </div>
            )}

            {/* Standard Scoring UI (Existing Code) */}

            <div className="assessment-card" style={{ borderLeft: '4px solid #0073BB' }}>
                <h3 style={{ marginBottom: '1.5rem', color: '#333333', fontSize: '11px', fontBold: 800, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Oracle Opportunity Context</h3>
                <div className="context-grid">
                    <div className="context-item">
                        <label className="text-[#666666]">Account</label>
                        <div className="text-[#333333] font-bold">{opp.customer_name || '-'}</div>
                    </div>
                    <div className="context-item">
                        <label className="text-[#666666]">Revenue (USD)</label>
                        <div className="text-[#217346] font-bold">${opp.deal_value?.toLocaleString() || '0'}</div>
                    </div>
                    <div className="context-item">
                        <label className="text-[#666666]">Sales Stage</label>
                        <div className="text-[#333333] font-bold">{opp.sales_stage || opp.stage || '-'}</div>
                    </div>
                    <div className="context-item">
                        <label className="text-[#666666]">Win Probability</label>
                        <div className="text-[#E27D12] font-bold">{opp.win_prob || opp.win_probability || 0}%</div>
                    </div>
                    <div className="context-item">
                        <label className="text-[#666666]">Sales Owner</label>
                        <div className="text-[#333333] font-bold">{opp.sales_owner_name || opp.sales_owner || '-'}</div>
                    </div>
                </div>
            </div>

            {/* Scoring Inputs (CRITERIA Loop) */}
            <div className="section-divider">
                <h2>Assessment Questionnaire</h2>
                <p>Rate the opportunity across the 8 key criteria below.</p>
            </div>

            <div className="assessment-card scoring-grid">
                {CRITERIA.map((c) => (
                    <div key={c.key} className="eval-card">
                        <div className="eval-header">
                            <h3>{c.label}</h3>
                            <div className="score-display">{(scores[c.key] || 3.0).toFixed(1)}</div>
                        </div>

                        <div className="slider-container">
                            <input
                                type="range"
                                min="0" max="5" step="0.5"
                                disabled={isReadOnly}
                                value={scores[c.key] || 3.0}
                                onChange={(e) => setScores({ ...scores, [c.key]: parseFloat(e.target.value) })}
                            />
                            <div className="slider-markers">
                                <span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
                            </div>
                        </div>

                        {/* Reason Chips (Simplified for brevity in replacement, keep usage) */}
                        <div className="reasons-section">
                            {/* ... existing chips logic ... */}
                            <div className="chips-container">
                                {((scores[c.key] || 3.0) <= 2.0 ? REASON_OPTIONS[c.key]?.low :
                                    (scores[c.key] || 3.0) >= 4.0 ? REASON_OPTIONS[c.key]?.high :
                                        REASON_OPTIONS[c.key]?.mid)?.map(reason => (
                                            <button
                                                key={reason}
                                                type="button"
                                                disabled={isReadOnly}
                                                onClick={() => {
                                                    const current = selectedReasons[c.key] || [];
                                                    const updated = current.includes(reason) ? current.filter(r => r !== reason) : [...current, reason];
                                                    setSelectedReasons({ ...selectedReasons, [c.key]: updated });
                                                }}
                                                className={`reason-chip ${(selectedReasons[c.key] || []).includes(reason) ? 'active' : ''}`}
                                            >
                                                {reason}
                                            </button>
                                        ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Final Summary & Actions */}
            <div className="summary-dark">
                {/* ... existing summary UI ... */}
                <div className="summary-metric">
                    <div>
                        <label>Weighted Score</label>
                        <div className="big-score">{weightedScore.toFixed(2)}</div>
                    </div>
                    <div>
                        <label>Verdict</label>
                        <div className={`verdict-badge ${verdict.class}`}>{verdict.label}</div>
                    </div>
                </div>
                <div className="summary-details">
                    <div className="justification-area">
                        <label className="flex items-center justify-between">
                            <span>Justification / Rationale (Mandatory) <span style={{ color: '#f87171' }}>*</span></span>
                        </label>
                        <textarea
                            placeholder="Explain the reasoning for this score..."
                            value={summary}
                            disabled={isLocked}
                            onChange={(e) => setSummary(e.target.value)}
                        />
                        <div className="upload-section">
                            <label style={{ fontSize: '12px', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 700, marginBottom: '15px', display: 'block' }}>Evidence / Attachments</label>
                            {attachmentName ? (
                                <div className="flex items-center gap-3 p-4 bg-white/5 border border-white/10 rounded-xl">
                                    <FileText className="text-blue-400" size={24} />
                                    <div className="flex-1 overflow-hidden">
                                        <p className="text-sm font-bold truncate">{attachmentName}</p>
                                        <p className="text-[10px] text-gray-400 font-bold uppercase tracking-tight">Evidence Attached</p>
                                    </div>
                                    {!isLocked && <button onClick={() => setAttachmentName(null)} className="text-rose-400 p-2 hover:bg-white/5 rounded-lg"><Trash2 size={16} /></button>}
                                </div>
                            ) : (
                                !isLocked && (
                                    <label className="custom-upload">
                                        <Upload size={20} className="text-blue-400" />
                                        <span style={{ fontSize: '14px', fontWeight: 700 }}>Upload Decision Document</span>
                                        <input type="file" className="hidden" onChange={handleFileUpload} />
                                    </label>
                                )
                            )}
                        </div>
                    </div>
                </div>

                <div className="action-bar">
                    <button className="btn-secondary" onClick={() => navigate(-1)}>Back</button>
                    <div className="flex gap-4">
                        {(isSA || isSP) && !isLocked && (
                            <>
                                <button className="btn-secondary" onClick={() => handleSave(false)} disabled={isSaving}>Save Draft</button>
                                <button className="btn-primary-enterprise" onClick={() => handleSave(true)} disabled={isSaving}>
                                    {isSaving ? 'Submitting...' : 'Submit Assessment'}
                                </button>
                            </>
                        )}
                        {isApprover && !combinedData && (['SUBMITTED', 'SUBMITTED_FOR_REVIEW', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED'].includes(status)) && (
                            <>
                                <button className="px-8 py-3 bg-[#A80000] text-white rounded font-bold uppercase transition-all hover:bg-red-800 shadow-lg" onClick={() => openApprovalModal('REJECT')} disabled={isSaving}>Reject</button>
                                <button className="px-8 py-3 bg-[#217346] text-white rounded font-bold uppercase transition-all hover:bg-green-800 shadow-lg" onClick={() => openApprovalModal('APPROVE')} disabled={isSaving}>Approve</button>
                            </>
                        )}
                    </div>
                </div>

                {/* History Section */}
                {history.length > 0 && (
                    <div className="log-section">
                        <div className="section-divider">
                            <h2>Assessment History</h2>
                            <p>Track all revisions and status changes for this deal.</p>
                        </div>
                        {history.map((h, i) => (
                            <div key={i} className="log-item">
                                <div className="log-meta">
                                    <span>REVISION #{h.version} — {h.status}</span>
                                    <span>{new Date(h.created_at).toLocaleString()}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: h.status === 'APPROVED' ? '#22c55e' : (h.status === 'REJECTED' ? '#ef4444' : '#f59e0b') }}></div>
                                                <span style={{ fontSize: '11px', fontWeight: 800, color: '#64748b', textTransform: 'uppercase' }}>
                                                    REVISION #{h.version} — {h.status}
                                                </span>
                                            </div>
                                            <button
                                                onClick={() => {
                                                    navigate(`/score/${id}?version=${h.version}`);
                                                    window.scrollTo(0, 0);
                                                }}
                                                className="text-[10px] font-bold text-[#0572CE] hover:text-blue-800 uppercase bg-blue-50 px-2 py-0.5 rounded border border-blue-100 transition-colors"
                                            >
                                                View Details
                                            </button>
                                        </div>
                                        <p style={{ fontSize: '14px', color: '#334155', fontWeight: 500 }}>{h.summary || "No rationale provided."}</p>
                                        <div style={{ marginTop: '10px', fontSize: '11px', color: '#94a3b8', fontWeight: 700 }}>SUBMITTED BY: {h.created_by}</div>
                                    </div>
                                    <div style={{ textAlign: 'right', marginLeft: '20px' }}>
                                        <div style={{ fontSize: '10px', color: '#94a3b8', fontWeight: 800 }}>RESULT</div>
                                        <div style={{ fontSize: '24px', fontWeight: 800, color: '#1e293b' }}>{h.score?.toFixed(2)}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <ApprovalModal
                isOpen={isApprovalModalOpen}
                onClose={() => setIsApprovalModalOpen(false)}
                onConfirm={handleModalConfirm}
                type={approvalAction || 'APPROVE'}
            />
        </div>
    );
};
