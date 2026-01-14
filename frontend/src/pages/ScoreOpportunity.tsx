
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export const ScoreOpportunity: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { currentUser } = useUser();

    const [opp, setOpp] = useState<any>(null);
    const [sections, setSections] = useState<any[]>([]);
    const [status, setStatus] = useState("NOT_STARTED");
    const [summary, setSummary] = useState("");
    const [confidence, setConfidence] = useState("MEDIUM");
    const [reco, setReco] = useState("PURSUE");

    useEffect(() => {
        const load = async () => {
            if (!id) return;
            // Details
            const d = await axios.get(`http://localhost:8000/api/inbox/${id}`);
            setOpp(d.data);

            // Score
            const s = await axios.get(`http://localhost:8000/api/scoring/${id}/latest`);
            if (s.data.sections) setSections(s.data.sections);
            if (s.data.status) setStatus(s.data.status);
            if (s.data.summary_comment) setSummary(s.data.summary_comment);
        };
        load();
    }, [id]);

    const handleChange = (idx: number, f: string, v: any) => {
        const n = [...sections];
        n[idx][f] = v;
        setSections(n);
    };

    const save = async (isSubmit: boolean) => {
        if (!currentUser) return;
        const payload = {
            user_id: currentUser.user_id,
            sections: sections.map(s => ({ section_code: s.section_code, score: parseInt(s.score), notes: s.notes })),
            confidence_level: confidence,
            recommendation: reco,
            summary_comment: summary
        };
        const url = `http://localhost:8000/api/scoring/${id}/${isSubmit ? 'submit' : 'draft'}`;
        await axios.post(url, payload);
        navigate('/');
    };

    if (!opp) return <div className="p-10">Loading...</div>;
    const isLocked = status === "SUBMITTED";

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white shadow my-6 rounded">
            <div className="flex justify-between items-start mb-6 border-b pb-4">
                <div>
                    <h1 className="text-2xl font-bold">{opp.opp_name}</h1>
                    <div className="text-gray-500">{opp.customer_name} | {opp.deal_value} USD</div>
                </div>
                <div className="px-3 py-1 bg-gray-100 rounded text-sm font-bold">{status}</div>
            </div>

            <div className="space-y-6">
                {sections.map((sec, i) => (
                    <div key={sec.section_code} className="p-4 border rounded bg-gray-50">
                        <div className="flex justify-between mb-2">
                            <label className="font-bold">{sec.section_name}</label>
                            <select disabled={isLocked} value={sec.score} onChange={e => handleChange(i, 'score', e.target.value)} className="border p-1 rounded">
                                <option value="0">-</option>
                                <option value="1">1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                            </select>
                        </div>
                        <textarea disabled={isLocked} value={sec.notes} onChange={e => handleChange(i, 'notes', e.target.value)} className="w-full border p-2 text-sm" placeholder="Notes..." />
                    </div>
                ))}
            </div>

            {!isLocked && (
                <div className="mt-6 flex justify-end gap-3">
                    <button onClick={() => save(false)} className="px-4 py-2 border rounded">Save Draft</button>
                    <button onClick={() => save(true)} className="px-4 py-2 bg-blue-600 text-white rounded">Submit</button>
                </div>
            )}
        </div>
    );
};
