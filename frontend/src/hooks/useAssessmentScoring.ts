
import { useMemo } from 'react';

export interface Section {
    section_code: string;
    section_name: string;
    weight: number;
    score: number;
    notes: string;
}

export type VerdictType = 'GO' | 'REVIEW' | 'NOGO';

export interface Verdict {
    label: string;
    type: VerdictType;
    colorClass: string;
    textColor: string;
    bgColor: string;
}

export const useAssessmentScoring = (sections: Section[]) => {

    // 1. Real-time Weighted Score Calculation
    const metrics = useMemo(() => {
        if (!sections || sections.length === 0) {
            return {
                weightedScore: 0,
                maxPossible: 0,
                percentage: 0
            };
        }

        let totalWeightedScore = 0;
        let totalWeight = 0;

        sections.forEach(section => {
            const score = Number(section.score) || 0;
            const weight = Number(section.weight) || 0;

            totalWeightedScore += (score * weight);
            totalWeight += weight;
        });

        // Backend Logic: max_s = total_w * 5 (since 5 is max score)
        const maxPossibleWeightedScore = totalWeight * 5;

        // Avoid division by zero
        const percentage = maxPossibleWeightedScore > 0
            ? Math.round((totalWeightedScore / maxPossibleWeightedScore) * 100)
            : 0;

        return {
            weightedScore: totalWeightedScore,
            maxPossible: maxPossibleWeightedScore,
            percentage
        };
    }, [sections]);

    // 2. Verdict Generation
    const verdict = useMemo((): Verdict => {
        const score = metrics.percentage;

        if (score >= 80) {
            return {
                label: "PURSUE AGGRESSIVELY",
                type: 'GO',
                colorClass: 'bg-green-100 border-green-500 text-green-800',
                textColor: 'text-green-700',
                bgColor: 'bg-green-100'
            };
        } else if (score >= 60) {
            return {
                label: "PURSUE WITH CAUTION",
                type: 'REVIEW',
                colorClass: 'bg-yellow-100 border-yellow-500 text-yellow-800',
                textColor: 'text-yellow-700',
                bgColor: 'bg-yellow-100'
            };
        } else {
            return {
                label: "NO GO / HIGH RISK",
                type: 'NOGO',
                colorClass: 'bg-red-100 border-red-500 text-red-800',
                textColor: 'text-red-700',
                bgColor: 'bg-red-100'
            };
        }
    }, [metrics.percentage]);

    return {
        ...metrics,
        verdict
    };
};
