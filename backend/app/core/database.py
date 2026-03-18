
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

from backend.app.models import Base, Role, AppUser, UserRole, OppScoreSection, OppScoreVersion, OppScoreSectionValue, Opportunity, OpportunityAssignment, Practice, SyncRun, SyncMeta, OracleOpportunity, DocumentCategory
from backend.app.core.logging_config import get_logger
from backend.app.core.self_healing import heal_database

logger = get_logger("database")


# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in the environment")

def init_db():
    """Checks if DB exists, creates it if not, and seeds initial data."""
    try:
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_PORT")
        
        # Connect to default 'postgres' db to check if 'bqs' exists
        conn = psycopg2.connect(dbname='postgres', user=db_user, host=db_host, password=db_password, port=db_port, connect_timeout=5)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bqs'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE bqs")
                logger.info("Database 'bqs' created.")
        conn.close()
    except Exception as e:
        logger.error(f"Startup DB Check: {e}")

    # Now connect to the actual DB
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    # Run Self-Healing before anything else
    try:
        heal_database(engine)
    except Exception as e:
        logger.error(f"Self-Healing Failed: {e}")

    echo=True
    Base.metadata.create_all(bind=engine)
    
    # Seed Data
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Roles - Read from INITIAL_ROLES env var (format: id:code:name,...)
        if not db.query(Role).first():
            roles_env = os.getenv("INITIAL_ROLES", "1:GH:Global Head,2:PH:Practice Head,3:SH:Sales Head,4:SA:Solution Architect,5:SP:Sales Person,6:PSH:Presales Head")
            roles_to_add = []
            for item in roles_env.split(","):
                try:
                    rid, rcode, rname = item.split(":")
                    roles_to_add.append(Role(role_id=int(rid), role_code=rcode, role_name=rname))
                except ValueError:
                    logger.warning(f"Invalid role format in INITIAL_ROLES: {item}")
            
            if roles_to_add:
                db.add_all(roles_to_add)
                db.flush()
                logger.info(f"Seeded {len(roles_to_add)} roles from environment.")

        # Sections - Synchronized with Frontend ScoreOpportunity.tsx
        # Task 2: Serve config from backend
        REASON_OPTIONS = {
            "STRAT": { 
                "critical": ["Extreme Misalignment", "Competitor Stronghold", "Legal/Regulatory Barrier"],
                "low": ["Geography Mismatch", "Technology Stack Mismatch", "Low Priority Region"],
                "average": ["Standard Offering", "Opportunistic Bid", "Minor Customization Needed"],
                "high": ["Target Client Account", "Strong Portfolio Addition", "Key Growth Area"],
                "exceptional": ["Board-Level Strategic Priority", "Market Entry Milestone", "CEO-Led Initiative"]
            },
            "WIN": {
                "critical": ["Late Entry (Post-RFP)", "Known RFP Bias", "Blacklisted by Client"],
                "low": ["Strong Incumbent", "No Capture History", "No Executive Access"],
                "average": ["Competitive Field", "Standard RFP Process", "Average Win Rate"],
                "high": ["Preferred Solution", "Niche Capability Leader", "Captured Early"],
                "exceptional": ["Single Source / Wired", "Exclusive Proof of Concept", "Incumbent with 100% Satisfaction"]
            },
            "COMP": {
                "critical": ["No Product Fit", "Worst-in-Class Feature Set", "Unproven Technology"],
                "low": ["Weak Positioning", "Generic Offering", "Low Brand Awareness"],
                "average": ["Top 3 Contender", "Equal Footing", "Standard Differentiators"],
                "high": ["Unique Value Prop", "Sole Source Potential", "Exclusive Partnership"],
                "exceptional": ["Unrivaled Tech Superiority", "Monopoly Position", "Patent Protected Solution"]
            },
            "FIN": {
                "critical": ["Negative Margin Deal", "Unfunded Project", "Unacceptable Terms"],
                "low": ["Low Margins", "High Cost of Sales", "Payment Terms Issue"],
                "average": ["Standard Margins", "Acceptable Budget", "Moderate CAPEX"],
                "high": ["High Margins", "Recurring Revenue Model", "Budget Approved/Funded"],
                "exceptional": ["Strategic Multi-Year Lock-in", "Massive TCV Upside", "Pre-Paid Contract"]
            },
            "FEAS": {
                "critical": ["Total Skill Mismatch", "Severe Talent Shortage", "Zero Infrastructure"],
                "low": ["Hiring Required", "Overbooked Experts", "Training Required"],
                "average": ["Partial Availability", "Subcontractors Needed", "Standard Lead Times"],
                "high": ["Team Bench Available", "Key Experts Ready", "Reusable Assets"],
                "exceptional": ["Fully Automated Delivery", "Global Team on Standby", "Plug-and-Play Implementation"]
            },
            "CUST": {
                "critical": ["Hostile Relationship", "Past Legal Dispute", "Direct Competitor Champion"],
                "low": ["No Previous Contact", "Cold Relationship", "Blocked by Gatekeeper"],
                "average": ["Transactional Contact", "New Stakeholders", "Neutral Reputation"],
                "high": ["Trusted Advisor Status", "Executive Sponsorship", "Coach in Account"],
                "exceptional": ["Partnership Alliance", "Shared Success Roadmap", "Co-Innovation Partner"]
            },
            "RISK": {
                "critical": ["High Probability Catastrophic Risk", "Sovereign Default Risk", "Criminal Liability"],
                "low": ["Undefined Scope", "Performance Penalties", "Complex Dependencies"],
                "average": ["Manageable Commercial Risk", "Standard Penalties", "Stable Environment"],
                "high": ["Well Defined Scope", "Stable Growth Area", "Low Dependencies"],
                "exceptional": ["Risk Transfer to Partner", "Zero Liability Clauses", "Fully Guaranteed Success"]
            },
            "PROD": {
                "critical": ["Major Regulatory Breach", "Security Red-Flag", "Zero Sovereignty"],
                "low": ["Non-Compliance", "Certifications Missing", "Workaround Required"],
                "average": ["Minor Deviation", "Waiver Potential", "Standard Data Handling"],
                "high": ["Fully Compliant", "Exceeds Standards", "Security Certified"],
                "exceptional": ["Gold Standard Industry Benchmark", "Pre-Approved by Regulator", "All Certs Active"]
            },
            "LEGAL": {
                "critical": ["Unlimited Liability", "No Termination Clause", "Loss of IP Control"],
                "low": ["Unfavorable Terms", "Bonding Issues", "Non-Standard SLA"],
                "average": ["Standard Terms", "Negotiable Clauses", "Acceptable Risk"],
                "high": ["Favorable Terms", "Pre-negotiated MSA", "IP Retained"],
                "exceptional": ["Standard Non-Negotiated MSA", "Zero IP Conflict", "Favorable Gov-Contract"]
            }
        }
        
        required_sections = [
            ("STRAT", "Strategic Fit", 1, 0.15),
            ("WIN", "Win Probability", 2, 0.15),
            ("FIN", "Financial Value", 3, 0.15),
            ("COMP", "Competitive Position", 4, 0.10),
            ("FEAS", "Delivery Feasibility", 5, 0.10),
            ("CUST", "Customer Relationship", 6, 0.10),
            ("RISK", "Risk Exposure", 7, 0.10),
            ("PROD", "Product / Service Compliance", 8, 0.05),
            ("LEGAL", "Legal & Commercial Readiness", 9, 0.10)
        ]
        
        for code, name, order, weight in required_sections:
            existing = db.query(OppScoreSection).filter_by(section_code=code).first()
            if not existing:
                db.add(OppScoreSection(
                    section_code=code, 
                    section_name=name, 
                    display_order=order, 
                    weight=weight,
                    reasons=REASON_OPTIONS.get(code, {})
                ))
            else:
                existing.section_name = name
                existing.display_order = order
                existing.weight = weight
                existing.reasons = REASON_OPTIONS.get(code, {})
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Seeding Error: {e}")
    finally:
        db.close()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
