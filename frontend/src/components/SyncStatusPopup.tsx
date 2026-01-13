
import React, { useState, useEffect } from 'react';
import { RefreshCcw, AlertCircle, CheckCircle, Clock, X, Terminal } from 'lucide-react';

interface SyncLog {
    id: number;
    sync_type: string;
    status: string;
    total_fetched: number;
    new_records: number;
    error_message: string | null;
    started_at: string;
    completed_at: string | null;
}

export const SyncStatusPopup: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
    const [logs, setLogs] = useState<SyncLog[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/v1/sync-logs');
            const data = await response.json();
            setLogs(data);
        } catch (error) {
            console.error('Failed to fetch sync logs:', error);
        } finally {
            setLoading(false);
        }
    };

    const triggerSync = async () => {
        try {
            await fetch('http://localhost:8000/api/v1/sync-crm', { method: 'POST' });
            alert('Sync triggered! Refresh logs in a few seconds.');
            fetchLogs();
        } catch (error) {
            alert('Failed to trigger sync');
        }
    };

    useEffect(() => {
        if (isOpen) {
            fetchLogs();
            const interval = setInterval(fetchLogs, 5000); // Polling every 5s while open
            return () => clearInterval(interval);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-full max-w-2xl bg-[#0f172a]/90 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
                {/* Header */}
                <div className="p-6 border-b border-white/10 flex justify-between items-center bg-gradient-to-r from-blue-600/10 to-indigo-600/10">
                    <div className="flex items-center gap-3">
                        <Terminal className="w-6 h-6 text-blue-400" />
                        <div>
                            <h2 className="text-xl font-bold text-white">CRM Sync Intelligence</h2>
                            <p className="text-sm text-slate-400">Live logs from Oracle CRM Integration</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs uppercase tracking-widest font-semibold text-slate-500">Recent Sync Cycles</span>
                        <div className="flex gap-2">
                            <button
                                onClick={fetchLogs}
                                className="text-xs flex items-center gap-1 text-blue-400 hover:text-blue-300 bg-blue-400/10 px-3 py-1 rounded-full px-2"
                            >
                                <RefreshCcw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                                Refresh
                            </button>
                            <button
                                onClick={triggerSync}
                                className="text-xs bg-white text-black font-bold px-3 py-1 rounded-full hover:bg-blue-50"
                            >
                                Trigger Manual Sync
                            </button>
                        </div>
                    </div>

                    {logs.length === 0 ? (
                        <div className="text-center py-12 border-2 border-dashed border-slate-800 rounded-xl">
                            <Clock className="w-12 h-12 text-slate-700 mx-auto mb-4" />
                            <p className="text-slate-500">No sync logs found. Trigger your first sync to see data.</p>
                        </div>
                    ) : (
                        logs.map((log) => (
                            <div
                                key={log.id}
                                className={`p-4 rounded-xl border transition-all ${log.status === 'FAILED'
                                        ? 'bg-red-500/5 border-red-500/20'
                                        : 'bg-emerald-500/5 border-emerald-500/20'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        {log.status === 'FAILED' ? (
                                            <AlertCircle className="w-5 h-5 text-red-500" />
                                        ) : (
                                            <CheckCircle className="w-5 h-5 text-emerald-500" />
                                        )}
                                        <span className="font-bold text-white uppercase text-xs tracking-wider">
                                            {log.sync_type} SYNC
                                        </span>
                                    </div>
                                    <span className="text-[10px] text-slate-500 font-mono">
                                        {new Date(log.started_at).toLocaleString()}
                                    </span>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mt-3">
                                    <div className="bg-white/5 p-2 rounded-lg">
                                        <p className="text-[10px] text-slate-500 uppercase">Records Fetched</p>
                                        <p className="text-lg font-bold text-white">{log.total_fetched}</p>
                                    </div>
                                    <div className="bg-white/5 p-2 rounded-lg">
                                        <p className="text-[10px] text-slate-500 uppercase">Status</p>
                                        <p className={`text-sm font-bold ${log.status === 'FAILED' ? 'text-red-400' : 'text-emerald-400'
                                            }`}>
                                            {log.status}
                                        </p>
                                    </div>
                                </div>

                                {log.error_message && (
                                    <div className="mt-4 p-3 bg-red-500/10 rounded-lg border border-red-500/20 flex gap-3">
                                        <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                                        <div className="overflow-hidden">
                                            <p className="text-xs font-bold text-red-300 uppercase mb-1">Critical Error</p>
                                            <p className="text-xs text-red-200/80 font-mono italic break-words leading-relaxed">
                                                {log.error_message}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 bg-white/5 border-t border-white/10 text-center">
                    <p className="text-[10px] text-slate-500 uppercase tracking-widest font-medium">
                        System Diagnostics • Verifying Oracle CRM API Integrity
                    </p>
                </div>
            </div>
        </div>
    );
};
