
export const REASON_OPTIONS: Record<string, { low: string[], mid: string[], high: string[] }> = {
    STRAT: { // Strategic Fit
        low: ["Outside Core Competency", "High Risk / Low Reward", "Misaligned with Roadmap", "Geography Mismatch", "Technology Stack Mismatch"],
        mid: ["Partial Strategic Fit", "Standard Offering", "Opportunistic Bid", "Minor Customization Needed", "Geography Adjacent"],
        high: ["Key Strategic Growth Area", "Strong Portfolio Addition", "Aligned with Core Biz", "Target Client Account", "Repeater Solution"]
    },
    WIN: { // Win Probability
        low: ["Unknown Client", "Late Entry", "Strong Incumbent", "RFP Bias Detected", "No Capture History"],
        mid: ["Known Client/Neutral", "Competitive Field", "Standard RFP Process", "Some Insider Info", "Average win rate"],
        high: ["Incumbent / Preferred", "Wired for Us", "Niche Capability Required", "Captured Early", "Client Requested Bid"]
    },
    COMP: { // Competitive Position
        low: ["Many Competitors", "Price-Sensitive Market", "Weak Positioning", "Generic Solution", "Low Brand Recognition"],
        mid: ["Top 3 Contender", "Equal Footing", "Standard Differentiation", "Price Competitive", "Known Brand"],
        high: ["Clear Market Leader", "Unique Value Prop", "Sole Source Potential", "High Barriers to Entry", "Exclusive Partnership"]
    },
    FIN: { // Financial Value
        low: ["Low Margins", "High Cost of Sales", "Unclear Budget", "Payment Terms Issue", "Currency Risk"],
        mid: ["Standard Margins", "Acceptable Budget", "Fixed Price Risk", "Standard Payment Terms", "Moderate CAPEX"],
        high: ["High Margins", "Recurring Revenue", "Budget Approved/Funded", "Upfront Payment", "Low CAPEX"]
    },
    RES: { // Resource Availability
        low: ["No Resources Available", "Hiring Required", "Skill Gap", "Overbooked Experts", "Visa/Travel Issues"],
        mid: ["Team Stretched", "Partial Availability", "Subcontractors Needed", "Training Required", "Remote/Onsite Mix"],
        high: ["Team Bench Available", "Key Experts Ready", "Reusable Assets", "Local Team Ready", "No Training Needed"]
    },
    PAST: { // Past Performance
        low: ["No Relevant CPARS", "Negative Past Feedback", "First Time Capability", "Litigation History", "No Referenceable Client"],
        mid: ["Similar Scale", "Verifiable References", "Good Track Record", "Partial Capability Match", "Neutral Feedback"],
        high: ["Exact Match Project", "Stellar References", "Award Winning Work", "Repeat Customer", "Case Study Available"]
    },
    CUST: { // Customer Relationship
        low: ["Cold Relationship", "Hostile Stakeholders", "No Previous Contact", "Blocked by Gatekeeper", "Competitor Champion"],
        mid: ["Transactional Relationship", "New Stakeholders", "Professional Acquaintance", "Neutral Stakeholders", "Past Contact"],
        high: ["Trusted Advisor", "Long-term Partner", "Executive Sponsorship", "Coach/Champion in Account", "Strategic Partner Status"]
    },
    LEGAL: { // Legal
        low: ["High Liability", "Unfavorable Terms", "Bonding Issue", "IP Ownership Risk", "Non-Standard SLA"],
        mid: ["Standard Terms", "Negotiable Clauses", "Acceptable Risk", "Standard SLA", "Insurance Covered"],
        high: ["Standard Contract", "Favorable Terms", "Pre-negotiated MSA", "No Liability Cap", "IP Retained"]
    }
};

export const CRITERIA_WEIGHTS: Record<string, number> = {
    STRAT: 0.15,
    WIN: 0.15,
    COMP: 0.15,
    FIN: 0.15,
    RES: 0.10,
    PAST: 0.10,
    CUST: 0.10,
    LEGAL: 0.10
};
