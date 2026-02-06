

export const REASON_OPTIONS: Record<string, { low: string[], mid: string[], high: string[] }> = {
    strategic_fit: { // Strategic Fit
        low: ["Outside Core Competency", "High Risk / Low Reward", "Misaligned with Roadmap", "Geography Mismatch", "Technology Stack Mismatch"],
        mid: ["Partial Strategic Fit", "Standard Offering", "Opportunistic Bid", "Minor Customization Needed", "Geography Adjacent"],
        high: ["Key Strategic Growth Area", "Strong Portfolio Addition", "Aligned with Core Biz", "Target Client Account", "Repeater Solution"]
    },
    win_probability: { // Win Probability
        low: ["Unknown Client", "Late Entry", "Strong Incumbent", "RFP Bias Detected", "No Capture History"],
        mid: ["Known Client/Neutral", "Competitive Field", "Standard RFP Process", "Some Insider Info", "Average win rate"],
        high: ["Incumbent / Preferred", "Wired for Us", "Niche Capability Required", "Captured Early", "Client Requested Bid"]
    },
    competitive_position: { // Competitive Position
        low: ["Many Competitors", "Price-Sensitive Market", "Weak Positioning", "Generic Solution", "Low Brand Recognition"],
        mid: ["Top 3 Contender", "Equal Footing", "Standard Differentiation", "Price Competitive", "Known Brand"],
        high: ["Clear Market Leader", "Unique Value Prop", "Sole Source Potential", "High Barriers to Entry", "Exclusive Partnership"]
    },
    financial_value: { // Financial Value
        low: ["Low Margins", "High Cost of Sales", "Unclear Budget", "Payment Terms Issue", "Currency Risk"],
        mid: ["Standard Margins", "Acceptable Budget", "Fixed Price Risk", "Standard Payment Terms", "Moderate CAPEX"],
        high: ["High Margins", "Recurring Revenue", "Budget Approved/Funded", "Upfront Payment", "Low CAPEX"]
    },
    delivery_feasibility: { // Delivery Feasibility (Mapped from old RES)
        low: ["No Resources Available", "Hiring Required", "Skill Gap", "Overbooked Experts", "Visa/Travel Issues"],
        mid: ["Team Stretched", "Partial Availability", "Subcontractors Needed", "Training Required", "Remote/Onsite Mix"],
        high: ["Team Bench Available", "Key Experts Ready", "Reusable Assets", "Local Team Ready", "No Training Needed"]
    },
    customer_relationship: { // Customer Relationship
        low: ["Cold Relationship", "Hostile Stakeholders", "No Previous Contact", "Blocked by Gatekeeper", "Competitor Champion"],
        mid: ["Transactional Relationship", "New Stakeholders", "Professional Acquaintance", "Neutral Stakeholders", "Past Contact"],
        high: ["Trusted Advisor", "Long-term Partner", "Executive Sponsorship", "Coach/Champion in Account", "Strategic Partner Status"]
    },
    risk_exposure: { // Risk Exposure (New)
        low: ["Significant Commercial Risk", "Undefined Scope", "Performance Penalties", "Political Instability", "Complex Dependencies"],
        mid: ["Manageable Commercial Risk", "Scope Requires Clarification", "Standard Penalties", "Stable Environment", "Some Dependencies"],
        high: ["Low Commercial Risk", "Well Defined Scope", "No Penalties", "Stable Growth Area", "Minimal Dependencies"]
    },
    compliance: { // Compliance (New)
        low: ["Major Non-Compliance", "Regulatory Blockers", "Security Gaps", "Data Sovereignty Issues", "Certifications Missing"],
        mid: ["Minor Non-Compliance", "Workaround Possible", "Security Waiver Needed", "Standard Data Handling", "Certifications Pending"],
        high: ["Fully Compliant", "Exceeds Standards", "Security Certified", "Data Localized", "All Certifications Active"]
    },
    legal_readiness: { // Legal & Commercial Readiness
        low: ["High Liability", "Unfavorable Terms", "Bonding Issue", "IP Ownership Risk", "Non-Standard SLA"],
        mid: ["Standard Terms", "Negotiable Clauses", "Acceptable Risk", "Standard SLA", "Insurance Covered"],
        high: ["Standard Contract", "Favorable Terms", "Pre-negotiated MSA", "No Liability Cap", "IP Retained"]
    }
};

export const CRITERIA_WEIGHTS: Record<string, number> = {
    strategic_fit: 0.15,
    win_probability: 0.15,
    financial_value: 0.15,
    competitive_position: 0.10,
    delivery_feasibility: 0.10,
    customer_relationship: 0.10,
    risk_exposure: 0.10,
    compliance: 0.05, // Lower weight as it's often binary
    legal_readiness: 0.10
};
