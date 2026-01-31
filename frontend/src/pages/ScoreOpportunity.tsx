
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { REASON_OPTIONS, CRITERIA_WEIGHTS } from '../constants/scoringCriteria';
import { ArrowLeft, Save, Send, AlertTriangle, FileText, Upload, Trash2, CheckCircle, Edit3, RefreshCw } from 'lucide-react';
import '../styles/Assessment.css';

const CRITERIA = [
    { key: "STRAT", label: "Strategic Fit/Why Inspira?", weight: 0.15 },
    { key: "WIN", label: "Win Probability", weight: 0.15 },
    { key: "COMP", label: "Competitive Position/Incumbent", weight: 0.15 },
    { key: "FIN", label: "Financial Value", weight: 0.15 },
    { key: "RES", label: "Resource Availability", weight: 0.10 },
    { key: "PAST", label: "Past Performance/References", weight: 0.10 },
    { key: "CUST", label: "Customer Relationship", weight: 0.10 },
    { key: "LEGAL", label: "Legal/Insurance/Bond Requirement", weight: 0.10 },
];

export const ScoreOpportunity: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const location = useLocation();
    const { user } = useAuth();

    // Core States
    const [opp, setOpp] = useState<any>(null);
    const [status, setStatus] = useState("NOT_STARTED");
    const [scores, setScores] = useState<Record<string, number>>({});
    const [selectedReasons, setSelectedReasons] = useState<Record<string, string[]>>({});
    const [sectionNotes, setSectionNotes] = useState<Record<string, string>>({});
    const [summary, setSummary] = useState("");
    const [confidence, setConfidence] = useState("MEDIUM");
    const [reco, setReco] = useState("PURSUE");
    const [attachmentName, setAttachmentName] = useState<string | null>(null);
    const [history, setHistory] = useState<any[]>([]);

    // UI/Flow States
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isIdentityEditable, setIsIdentityEditable] = useState(false);
    const [deadline, setDeadline] = useState("");

    const isPH = user?.role === 'PRACTICE_HEAD';
    const isSA = user?.role === 'SOLUTION_ARCHITECT';

    const isEdit = status !== "NOT_STARTED";
    const isLocked = status === "SUBMITTED" || status === "APPROVED" || status === "REJECTED";
    const isReadOnly = isPH || isLocked;

    // Deadline check: only allow new versions if deadline is not passed
    const isDeadlinePassed = deadline ? new Date(deadline + 'T23:59:59') < new Date() : false;

    useEffect(() => {
        const load = async () => {
            if (!id) return;
            try {
                // 1. Fetch Opportunity Context
                const d = await axios.get(`http://127.0.0.1:8000/api/inbox/${id}`);
                setOpp(d.data);
                if (d.data.close_date) {
                    setDeadline(new Date(d.data.close_date).toISOString().split('T')[0]);
                }

                // 2. Fetch Latest Assessment Data
                const s = await axios.get(`http://127.0.0.1:8000/api/scoring/${id}/latest`);
                if (s.data.status !== "NOT_STARTED") {
                    setStatus(s.data.status);
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
                } else {
                    // Initialize with 3.0
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
    }, [id]);

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
        if (isSubmit && (!summary || summary.trim().length < 5)) {
            alert("A detailed Justification Rationale is MANDATORY for submission.");
            return;
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
            navigate(isSubmit ? '/architect/submitted' : '/architect/assigned');
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

    const handleApprove = async () => {
        if (!confirm("Approve this assessment?")) return;
        setIsSaving(true);
        try {
            await axios.post(`http://127.0.0.1:8000/api/scoring/${id}/review/approve`);
            alert("Assessment Approved.");
            navigate('/practice-head/review');
        } catch (err) {
            alert("Approval failed.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleReject = async () => {
        const reason = prompt("Enter rejection reason:");
        if (!reason) return;
        setIsSaving(true);
        try {
            await axios.post(`http://127.0.0.1:8000/api/scoring/${id}/review/reject`, { reason });
            alert("Assessment Rejected.");
            navigate('/practice-head/review');
        } catch (err) {
            alert("Rejection failed.");
        } finally {
            setIsSaving(false);
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

    // Previous Assessment Logic
    const previousAssessment = history.length > 0 ? history[0] : null;

    return (
        <div className="assessment-root animate-fade">
            <header className="assessment-header">
                <div className="header-title-group">
                    <button className="back-btn-circle" onClick={() => navigate(-1)}><ArrowLeft size={20} /></button>
                    <div>
                        <h1 style={{ fontFamily: '"Libre Baskerville", serif', fontSize: '28px', color: '#333333' }}>
                            {isReadOnly ? 'View Assessment' : (isEdit ? 'Fill Assessment' : 'New Assessment')}
                        </h1>
                        <p className="header-subtitle" style={{ color: '#666666', fontWeight: 500 }}>Bid Qualification and Scoring Form</p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    {isSA && isLocked && !isDeadlinePassed && (
                        <button
                            onClick={handleNewVersion}
                            className="flex items-center gap-1 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-bold hover:bg-blue-100 transition-all shadow-sm"
                        >
                            <RefreshCw size={14} className="animate-spin-slow" /> Create New Version
                        </button>
                    )}
                    {isSA && isLocked && status === 'SUBMITTED' && (
                        <button
                            onClick={handleReopen}
                            className="flex items-center gap-1 px-4 py-2 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-bold hover:bg-amber-100 transition-colors"
                        >
                            <Edit3 size={14} /> Re-open Draft
                        </button>
                    )}
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 800, textTransform: 'uppercase' }}>STATUS</div>
                        <div style={{ fontWeight: 800, color: isLocked ? '#2e7d32' : '#0073BB', fontSize: '14px' }}>{status}</div>
                    </div>
                    <div className="assessment-id-badge" style={{ backgroundColor: '#f1f5f9', padding: '10px 20px', borderRadius: '12px', fontWeight: 800, fontSize: '12px' }}>
                        ID: {opp.opp_id}
                    </div>
                </div>
            </header>

            {/* Oracle Context Card */}
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

            {/* Previous Scoring Summary (Top View) */}
            {previousAssessment && (
                <div className="assessment-card" style={{ borderLeft: '4px solid #7c3aed', backgroundColor: '#f5f3ff' }}>
                    <div className="flex justify-between items-center mb-4">
                        <h3 style={{ color: '#5b21b6', fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Previous Assessment • {new Date(previousAssessment.created_at).toLocaleDateString()}
                        </h3>
                        <span className="text-xs font-bold px-2 py-1 rounded bg-white text-violet-700 border border-violet-200">
                            VERSION {previousAssessment.version}
                        </span>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-4">
                        <div>
                            <label className="text-xs font-bold text-violet-500 uppercase block mb-1">Prior Score</label>
                            <span className="text-2xl font-black text-violet-900">{previousAssessment.score?.toFixed(2)}</span>
                        </div>
                        <div className="col-span-2">
                            <label className="text-xs font-bold text-violet-500 uppercase block mb-1">Prior Recommendation</label>
                            <span className="text-sm font-bold text-violet-800 bg-white px-2 py-1 rounded border border-violet-100 shadow-sm inline-block">
                                {previousAssessment.recommendation}
                            </span>
                        </div>
                        <div>
                            <label className="text-xs font-bold text-violet-500 uppercase block mb-1">Assessed By</label>
                            <span className="text-sm font-medium text-violet-800">{previousAssessment.created_by?.split('-')[0]}</span>
                        </div>
                    </div>

                    <div>
                        <label className="text-xs font-bold text-violet-500 uppercase block mb-1">Prior Rationale</label>
                        <p className="text-sm text-violet-800 italic bg-white/50 p-2 rounded border-l-2 border-violet-300">
                            "{previousAssessment.summary || 'No summary provided.'}"
                        </p>
                    </div>
                </div>
            )}

            {/* Identity & Scope Card */}
            <div className="assessment-card">
                <div className="input-group">
                    <div className="field-box">
                        <label>Opportunity ID</label>
                        <input value={opp.opp_id} disabled style={{ backgroundColor: '#f0fdf4', color: '#166534' }} />
                    </div>
                    <div className="field-box">
                        <label>Assessment Scope</label>
                        <input
                            value={opp.opp_name}
                            disabled={!isIdentityEditable || isLocked}
                            onChange={(e) => setOpp({ ...opp, opp_name: e.target.value })}
                        />
                    </div>
                    <div className="field-box">
                        <label>Completion Deadline</label>
                        <input
                            type="date"
                            value={deadline}
                            disabled={!isIdentityEditable || isReadOnly}
                            onChange={(e) => setDeadline(e.target.value)}
                        />
                    </div>
                </div>
                <div style={{ marginTop: '25px', display: 'flex', justifyContent: 'flex-end' }}>
                    {!isReadOnly && (
                        <button className="unlock-link-soft" onClick={() => setIsIdentityEditable(!isIdentityEditable)}>
                            {isIdentityEditable ? <><CheckCircle size={16} /> Save Identity</> : <><Edit3 size={16} /> Modify Identity</>}
                        </button>
                    )}
                </div>
            </div>

            <div className="section-divider">
                <h2>Assessment Questionnaire</h2>
                <p>Rate the opportunity across the 8 key criteria below.</p>
            </div>

            {/* Scoring Area */}
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

                        <div className="reasons-section">
                            <label>Supporting Indicators (Why {(scores[c.key] || 3.0).toFixed(1)}?)</label>
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

            {/* Final Summary */}
            <div className="summary-dark">
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
                        <label>Justification / Rationale (Mandatory) <span style={{ color: '#f87171' }}>*</span></label>
                        <textarea
                            placeholder="Explain the reasoning for this score..."
                            value={summary}
                            disabled={isLocked}
                            onChange={(e) => setSummary(e.target.value)}
                        />
                    </div>

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
                <button className="btn-secondary" onClick={() => navigate(-1)}>Back to Dashboard</button>
                <div className="flex gap-4">
                    {isSA && !isLocked && (
                        <>
                            <button className="btn-secondary" onClick={() => handleSave(false)} disabled={isSaving}>Save Draft</button>
                            <button className="btn-primary-enterprise" onClick={() => handleSave(true)} disabled={isSaving}>
                                {isSaving ? 'Submitting...' : 'Submit Assessment'}
                            </button>
                        </>
                    )}
                    {isPH && status === 'SUBMITTED' && (
                        <>
                            <button className="px-8 py-3 bg-[#A80000] text-white rounded font-bold uppercase transition-all hover:bg-red-800 shadow-lg" onClick={handleReject} disabled={isSaving}>Reject Assessment</button>
                            <button className="px-8 py-3 bg-[#217346] text-white rounded font-bold uppercase transition-all hover:bg-green-800 shadow-lg" onClick={handleApprove} disabled={isSaving}>Approve Assessment</button>
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
                                    <p style={{ fontSize: '14px', color: '#334155', fontWeight: 500 }}>{h.summary || "No rationale provided."}</p>
                                    <div style={{ marginTop: '10px', fontSize: '11px', color: '#94a3b8', fontWeight: 700 }}>BY ARCHITECT: {h.created_by.split('-')[0]}</div>
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
    );
};
