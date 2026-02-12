
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
    const isReadOnly = isLocked || isUserSubmitted || (isApprover && status !== 'NOT_STARTED' && status !== 'DRAFT');

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
                    CRITERIA.forEach(c => initialScores[c.key] = 3.0);
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

    if (loading) return <div className="p-loader">Retrieving Critical Data...</div>;
    if (!opp) return <div className="p-loader text-red-500">Opportunity Not Found</div>;

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
                        <div className="flex gap-3">
                            <button onClick={() => openApprovalModal('REJECT')} className="px-6 py-2 bg-red-100 text-red-700 font-bold rounded hover:bg-red-200">REJECT</button>
                            <button onClick={() => openApprovalModal('APPROVE')} className="px-6 py-2 bg-green-600 text-white font-bold rounded hover:bg-green-700 shadow-md">APPROVE</button>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-8">
                        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-blue-500">
                            <h2 className="text-lg font-bold text-gray-800 mb-4">Solution Architect</h2>
                            <div className="text-4xl font-black text-gray-900 mb-6">{combinedData?.sa_assessment?.score || 0}%</div>
                            {/* Render SA Scores */}
                        </div>
                        <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-purple-500">
                            <h2 className="text-lg font-bold text-gray-800 mb-4">Sales Person</h2>
                            <div className="text-4xl font-black text-gray-900 mb-6">{combinedData?.sp_assessment?.score || 0}%</div>
                            {/* Render SP Scores */}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="assessment-root animate-fade">
            <header className="assessment-header">
                <div className="header-title-group">
                    <button className="back-btn-circle" onClick={() => navigate(-1)}><ArrowLeft size={20} /></button>
                    <div>
                        <h1 style={{ fontFamily: '"Libre Baskerville", serif', fontSize: '28px', color: '#333333' }}>
                            {isLocked ? 'View Finalized Assessment' : (currentVersion && currentVersion > 1 ? 'Update Assessment Version' : 'New Assessment')}
                        </h1>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    {(isSA || isSP) && isLocked && !isDeadlinePassed && (
                        <button onClick={handleNewVersion} className="flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 shadow-sm">
                            <RefreshCw size={14} /> Create New Version
                        </button>
                    )}
                </div>
            </header>

            {isLocked && (
                <div className="bg-amber-600 text-white px-6 py-2 font-black text-center text-xs tracking-[0.2em] uppercase mb-4 rounded shadow-lg">
                    ⚠️ READ ONLY RECORD - Assessment Finalized
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
                        <label className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-1">Win Probability</label>
                        <div className="text-lg font-bold text-orange-500">{opp.win_prob || opp.win_probability || 0}%</div>
                    </div>
                </div>
            </div>

            <div className="section-divider mb-8 mt-12 px-6">
                <h2 className="text-xl font-black text-gray-900">Assessment Questionnaire</h2>
                <p className="text-gray-500">Rate the opportunity across the key criteria below.</p>
            </div>

            <div className="scoring-grid grid grid-cols-1 gap-6 px-6">
                {CRITERIA.map((c) => (
                    <div key={c.key} className="eval-card bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div className="eval-header flex justify-between items-center mb-6">
                            <h3 className="text-lg font-bold text-gray-900">{c.label}</h3>
                            <div className="score-display text-2xl font-black text-blue-600">{(scores[c.key] || 3.0).toFixed(1)}</div>
                        </div>
                        <input
                            type="range"
                            min="0" max="5" step="0.5"
                            disabled={isReadOnly}
                            value={scores[c.key] || 3.0}
                            onChange={(e) => setScores({ ...scores, [c.key]: parseFloat(e.target.value) })}
                            className="w-full h-2 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <textarea
                            className="w-full mt-6 p-4 bg-gray-50 border border-gray-100 rounded-xl text-sm italic outline-none focus:border-blue-500"
                            placeholder={`Rationale for ${c.label}...`}
                            value={sectionNotes[c.key] || ""}
                            disabled={isReadOnly}
                            onChange={(e) => setSectionNotes({ ...sectionNotes, [c.key]: e.target.value })}
                        />
                    </div>
                ))}
            </div>

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
                        {!isLocked && !isUserSubmitted && (
                            <>
                                <button className="px-10 py-4 bg-white/5 border border-white/10 rounded-2xl font-bold hover:bg-white/10" onClick={() => handleSave(false)}>Save Draft</button>
                                <button className="px-10 py-4 bg-blue-600 rounded-2xl font-black hover:bg-blue-700 shadow-xl" onClick={() => handleSave(true)}>Submit Assessment</button>
                            </>
                        )}
                        {isApprover && !combinedData && ['SUBMITTED', 'READY_FOR_REVIEW'].includes(status) && (
                            <>
                                <button className="px-10 py-4 bg-red-600 rounded-2xl font-black hover:bg-red-700 shadow-xl" onClick={() => openApprovalModal('REJECT')}>Reject</button>
                                <button className="px-10 py-4 bg-green-600 rounded-2xl font-black hover:bg-green-700 shadow-xl" onClick={() => openApprovalModal('APPROVE')}>Approve</button>
                            </>
                        )}
                    </div>
                </div>
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
