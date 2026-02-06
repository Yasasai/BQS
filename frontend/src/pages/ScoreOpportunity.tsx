
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { REASON_OPTIONS, CRITERIA_WEIGHTS } from '../constants/scoringCriteria';
import { ArrowLeft, Save, Send, AlertTriangle, FileText, Upload, Trash2, CheckCircle, Edit3, RefreshCw } from 'lucide-react';
import '../styles/Assessment.css';

const CRITERIA = [
    { key: "strategic_fit", label: "Strategic Fit", weight: 0.15 },
    { key: "win_probability", label: "Win Probability", weight: 0.15 },
    { key: "financial_value", label: "Financial Value", weight: 0.15 },
    { key: "competitive_position", label: "Competitive Position", weight: 0.10 },
    { key: "delivery_feasibility", label: "Delivery Feasibility", weight: 0.10 },
    { key: "customer_relationship", label: "Customer Relationship", weight: 0.10 },
    { key: "risk_exposure", label: "Risk Exposure", weight: 0.10 },
    { key: "compliance", label: "Product / Service Compliance", weight: 0.05 },
    { key: "legal_readiness", label: "Legal & Commercial Readiness", weight: 0.10 },
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
    const [reco, setReco] = useState("PURSUE");
    const [attachmentName, setAttachmentName] = useState<string | null>(null);
    const [history, setHistory] = useState<any[]>([]);

    // UI/Flow States
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [isIdentityEditable, setIsIdentityEditable] = useState(false);
    const [deadline, setDeadline] = useState("");

    const isPH = user?.role === 'PH';
    const isSA = user?.role === 'SA' || user?.role === 'SP';

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

    return (
        <div className="assessment-root animate-fade">
            <header className="assessment-header">
                <div className="header-title-group">
                    <button className="back-btn-circle" onClick={() => navigate(isPH ? '/' : '/assigned-to-me')}><ArrowLeft size={20} /></button>
                    <div>
                        <h1 style={{ fontFamily: '"Libre Baskerville", serif', fontSize: '28px', color: '#333333' }}>
                            {isLocked ? 'View Finalized Assessment' : (currentVersion && currentVersion > 1 ? 'Update Assessment Version' : 'New Assessment')}
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
                    <div style={{ textAlign: 'center', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em' }}>CURRENT STATUS</div>
                        <div style={{ fontWeight: 900, color: status === 'REJECTED' ? '#ef4444' : (isLocked ? '#2e7d32' : '#0572CE'), fontSize: '20px', textTransform: 'uppercase' }}>{status.replace(/_/g, ' ')}</div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                        <div className="assessment-id-badge" style={{ backgroundColor: '#f1f5f9', padding: '6px 15px', borderRadius: '8px', fontWeight: 800, fontSize: '12px', color: '#334155', border: '1px solid #e2e8f0' }}>
                            OPP ID: {opp.opp_id}
                        </div>
                        {currentVersion && (
                            <div style={{ fontSize: '11px', fontWeight: 800, color: '#475569', backgroundColor: '#f8fafc', padding: '2px 8px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                                VERSION {currentVersion}
                            </div>
                        )}
                    </div>
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
                            <p className="text-sm opacity-90">Previously assessed values have been cloned for your reference. Please update and submit the new version.</p>
                        </div>
                    </div>
                    <div className="bg-white/10 px-4 py-2 rounded-lg font-bold text-sm">Action Required</div>
                </div>
            )}

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

            {/* Previous Scoring Summary (Top View) - Lavender Styling matching image */}
            {prevAssessment && (
                <div className="assessment-card" style={{ borderLeft: '5px solid #7c3aed', backgroundColor: '#f5f3ff', padding: '24px' }}>
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-3">
                            <h3 style={{ color: '#6b21a8', fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                PREVIOUS ASSESSMENT • {new Date(prevAssessment.created_at).toLocaleDateString()}
                            </h3>
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded uppercase tracking-tighter ${prevAssessment.status === 'REJECTED' ? 'bg-rose-500 text-white' : 'bg-emerald-500 text-white'
                                }`}>
                                {prevAssessment.status}
                            </span>
                        </div>
                        <span className="text-[11px] font-bold px-3 py-1 rounded border border-purple-200 text-purple-700 bg-white shadow-sm uppercase">
                            VERSION {prevAssessment.version_no}
                        </span>
                    </div>

                    <div className="grid grid-cols-4 gap-8 mb-6">
                        <div>
                            <label className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block mb-2">PRIOR SCORE</label>
                            <span className="text-3xl font-black text-purple-900 leading-none">{prevAssessment.overall_score}.00</span>
                        </div>
                        <div className="col-span-1">
                            <label className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block mb-2">PRIOR RECOMMENDATION</label>
                            <span className="text-[13px] font-bold text-purple-800 bg-white px-3 py-1.5 rounded border border-purple-100 shadow-sm inline-block">
                                {prevAssessment.recommendation || 'NOT DEFINED'}
                            </span>
                        </div>
                        <div className="col-span-2 text-right">
                            <label className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block mb-2">ASSESSED BY</label>
                            <span className="text-sm font-bold text-purple-800">{prevAssessment.created_by || 'b635f96'}</span>
                        </div>
                    </div>

                    <div style={{ marginTop: '15px' }}>
                        <label className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block mb-2">PRIOR RATIONALE</label>
                        <div className="p-4 rounded-lg bg-white/60 border-l-4 border-purple-200 shadow-inner">
                            <p className="text-[14px] text-purple-800 font-medium italic leading-relaxed">
                                "{prevAssessment.summary_comment || 'Check on backend and give needed updates now'}"
                            </p>
                        </div>
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
                        <label className="flex items-center justify-between">
                            <span>{currentVersion && currentVersion > 1 ? 'New Version Justification / Rationale' : 'Justification / Rationale'} (Mandatory) <span style={{ color: '#f87171' }}>*</span></span>
                            {currentVersion && currentVersion > 1 && <span className="text-[10px] bg-blue-100 text-blue-700 font-bold px-2 py-0.5 rounded">UPDATES REQUIRED</span>}
                        </label>
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
                <button
                    className="btn-secondary"
                    onClick={() => navigate(isPH ? '/' : '/assigned-to-me')}
                >
                    Back to Dashboard
                </button>                <div className="flex gap-4">
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
