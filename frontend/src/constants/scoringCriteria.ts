

export const REASON_OPTIONS: Record<string, { critical: string[], low: string[], average: string[], high: string[], exceptional: string[] }> = {
    STRAT: { // Strategic Fit
        critical: ["Extreme Misalignment", "Competitor Stronghold", "Legal/Regulatory Barrier"],
        low: ["Geography Mismatch", "Technology Stack Mismatch", "Low Priority Region"],
        average: ["Standard Offering", "Opportunistic Bid", "Minor Customization Needed"],
        high: ["Target Client Account", "Strong Portfolio Addition", "Key Growth Area"],
        exceptional: ["Board-Level Strategic Priority", "Market Entry Milestone", "CEO-Led Initiative"]
    },
    WIN: { // Win Probability
        critical: ["Late Entry (Post-RFP)", "Known RFP Bias", "Blacklisted by Client"],
        low: ["Strong Incumbent", "No Capture History", "No Executive Access"],
        average: ["Competitive Field", "Standard RFP Process", "Average Win Rate"],
        high: ["Preferred Solution", "Niche Capability Leader", "Captured Early"],
        exceptional: ["Single Source / Wired", "Exclusive Proof of Concept", "Incumbent with 100% Satisfaction"]
    },
    COMP: { // Competitive Position
        critical: ["No Product Fit", "Worst-in-Class Feature Set", "Unproven Technology"],
        low: ["Weak Positioning", "Generic Offering", "Low Brand Awareness"],
        average: ["Top 3 Contender", "Equal Footing", "Standard Differentiators"],
        high: ["Unique Value Prop", "Sole Source Potential", "Exclusive Partnership"],
        exceptional: ["Unrivaled Tech Superiority", "Monopoly Position", "Patent Protected Solution"]
    },
    FIN: { // Financial Value
        critical: ["Negative Margin Deal", "Unfunded Project", "Unacceptable Terms"],
        low: ["Low Margins", "High Cost of Sales", "Payment Terms Issue"],
        average: ["Standard Margins", "Acceptable Budget", "Moderate CAPEX"],
        high: ["High Margins", "Recurring Revenue Model", "Budget Approved/Funded"],
        exceptional: ["Strategic Multi-Year Lock-in", "Massive TCV Upside", "Pre-Paid Contract"]
    },
    FEAS: { // Delivery Feasibility
        critical: ["Total Skill Mismatch", "Severe Talent Shortage", "Zero Infrastructure"],
        low: ["Hiring Required", "Overbooked Experts", "Training Required"],
        average: ["Partial Availability", "Subcontractors Needed", "Standard Lead Times"],
        high: ["Team Bench Available", "Key Experts Ready", "Reusable Assets"],
        exceptional: ["Fully Automated Delivery", "Global Team on Standby", "Plug-and-Play Implementation"]
    },
    CUST: { // Customer Relationship
        critical: ["Hostile Relationship", "Past Legal Dispute", "Direct Competitor Champion"],
        low: ["No Previous Contact", "Cold Relationship", "Blocked by Gatekeeper"],
        average: ["Transactional Contact", "New Stakeholders", "Neutral Reputation"],
        high: ["Trusted Advisor Status", "Executive Sponsorship", "Coach in Account"],
        exceptional: ["Partnership Alliance", "Shared Success Roadmap", "Co-Innovation Partner"]
    },
    RISK: { // Risk Exposure
        critical: ["High Probability Catastrophic Risk", "Sovereign Default Risk", "Criminal Liability"],
        low: ["Undefined Scope", "Performance Penalties", "Complex Dependencies"],
        average: ["Manageable Commercial Risk", "Standard Penalties", "Stable Environment"],
        high: ["Well Defined Scope", "Stable Growth Area", "Low Dependencies"],
        exceptional: ["Risk Transfer to Partner", "Zero Liability Clauses", "Fully Guaranteed Success"]
    },
    PROD: { // Product / Service Compliance
        critical: ["Major Regulatory Breach", "Security Red-Flag", "Zero Sovereignty"],
        low: ["Non-Compliance", "Certifications Missing", "Workaround Required"],
        average: ["Minor Deviation", "Waiver Potential", "Standard Data Handling"],
        high: ["Fully Compliant", "Exceeds Standards", "Security Certified"],
        exceptional: ["Gold Standard Industry Benchmark", "Pre-Approved by Regulator", "All Certs Active"]
    },
    LEGAL: { // Legal & Commercial Readiness
        critical: ["Unlimited Liability", "No Termination Clause", "Loss of IP Control"],
        low: ["Unfavorable Terms", "Bonding Issues", "Non-Standard SLA"],
        average: ["Standard Terms", "Negotiable Clauses", "Acceptable Risk"],
        high: ["Favorable Terms", "Pre-negotiated MSA", "IP Retained"],
        exceptional: ["Standard Non-Negotiated MSA", "Zero IP Conflict", "Favorable Gov-Contract"]
    }
};

export const CRITERIA_WEIGHTS: Record<string, number> = {
    STRAT: 0.15,
    WIN: 0.15,
    FIN: 0.15,
    COMP: 0.10,
    FEAS: 0.10,
    CUST: 0.10,
    RISK: 0.10,
    PROD: 0.05,
    LEGAL: 0.10
};
