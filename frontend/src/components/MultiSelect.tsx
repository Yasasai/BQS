import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Check } from 'lucide-react';

interface Option {
    label: string;
    value: string;
    count?: number;
}

interface MultiSelectProps {
    options: Option[];
    selected: string[];
    onChange: (values: string[]) => void;
    placeholder?: string;
    label?: string;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({ options, selected, onChange, placeholder = "Select...", label }) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const toggleOption = (val: string) => {
        if (selected.includes(val)) {
            onChange(selected.filter(v => v !== val));
        } else {
            onChange([...selected, val]);
        }
    };

    const clearAll = (e: React.MouseEvent) => {
        e.stopPropagation();
        onChange([]);
    };

    return (
        <div className="flex flex-col gap-1 min-w-[200px]" ref={containerRef}>
            {label && <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{label}</span>}
            <div
                className={`relative flex items-center justify-between bg-white border ${isOpen ? 'border-blue-500 ring-2 ring-blue-500/10' : 'border-gray-300'} rounded px-2 py-1.5 cursor-pointer transition-all h-8`}
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex gap-1 overflow-hidden">
                    {selected.length === 0 ? (
                        <span className="text-gray-400 text-xs truncate">{placeholder}</span>
                    ) : (
                        <div className="flex gap-1">
                            {selected.slice(0, 2).map(val => {
                                const opt = options.find(o => o.value === val);
                                return (
                                    <span key={val} className="bg-blue-50 text-blue-700 text-[10px] px-1.5 py-0.5 rounded-sm flex items-center gap-1 border border-blue-100">
                                        {opt?.label}
                                        <X size={10} className="hover:text-blue-900" onClick={(e) => { e.stopPropagation(); toggleOption(val); }} />
                                    </span>
                                );
                            })}
                            {selected.length > 2 && <span className="text-[10px] text-gray-500 font-bold">+{selected.length - 2}</span>}
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-1 ml-2">
                    {selected.length > 0 && <X size={12} className="text-gray-400 hover:text-gray-600" onClick={clearAll} />}
                    <ChevronDown size={14} className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </div>

                {isOpen && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 shadow-xl rounded-sm z-[100] max-h-60 overflow-y-auto animate-in fade-in slide-in-from-top-1 duration-200">
                        {options.map(opt => (
                            <div
                                key={opt.value}
                                className={`flex items-center justify-between px-3 py-2 hover:bg-gray-50 text-xs ${selected.includes(opt.value) ? 'bg-blue-50/50 text-blue-700' : 'text-gray-700'}`}
                                onClick={(e) => { e.stopPropagation(); toggleOption(opt.value); }}
                            >
                                <div className="flex items-center gap-2">
                                    <div className={`w-3.5 h-3.5 border rounded-sm flex items-center justify-center transition-colors ${selected.includes(opt.value) ? 'bg-blue-600 border-blue-600' : 'border-gray-300'}`}>
                                        {selected.includes(opt.value) && <Check size={10} className="text-white" />}
                                    </div>
                                    <span className={selected.includes(opt.value) ? 'font-bold' : ''}>{opt.label}</span>
                                </div>
                                {opt.count !== undefined && <span className="text-[10px] text-gray-400 bg-gray-100 px-1 rounded-full">{opt.count}</span>}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
