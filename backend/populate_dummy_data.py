"""
Premium Dummy Data Generator for BQS. 
Populates 100% compliant data for the 3-role workflow.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Opportunity, Assessment, User, init_db

def populate():
    print("="*60)
    print("🌟 BQS PREMIUM DATA POPULATOR")
    print("="*60)

    db = SessionLocal()
    try:
        # 1. Clear Data
        print("\n[1/4] Clearing stale data...")
        db.query(Assessment).delete()
        db.query(Opportunity).delete()
        db.query(User).delete()
        db.commit()

        # 2. Create Users
        print("[2/4] Seeding workflow users...")
        sa_list = ["Jane Smith", "Michael Chen", "David Wilson"]
        for name in sa_list:
            db.add(User(email=f"{name.lower().replace(' ', '.')}@company.com", name=name, role="Solution Architect"))
        db.add(User(email="management@company.com", name="Executive User", role="Management"))
        db.add(User(email="practice.head@company.com", name="John Doe", role="Practice Head"))
        db.commit()

        # 3. Create Opportunities
        print("[3/4] Generating 25 workflow-diverse opportunities...")
        
        customers = ["JPMorgan", "FedEx", "Coca Cola", "Tesla", "Apple", "Google", "Amazon", "Netflix"]
        practices = ["Cloud Infrastructure", "Cybersecurity", "Data Analytics", "AI/ML"]
        
        # Every possible status in the system
        all_statuses = [
            "NEW",                     # Stage 1: Triage
            "ASSIGNED_TO_PRACTICE",    # Stage 2: PH Allocation
            "PENDING_ASSESSMENT",      # Stage 3: SA Pending
            "UNDER_ASSESSMENT",        # Stage 4: SA Working
            "REVIEW_PENDING",          # Stage 5: PH Review
            "PENDING_GOVERNANCE",      # Stage 6: Management Decision
            "COMPLETED_BID",           # Stage 7: History (Won)
            "COMPLETED_NO_BID"         # Stage 7: History (Lost/No-Go)
        ]

        for i in range(25):
            status = random.choice(all_statuses)
            customer = random.choice(customers)
            
            # Logic to make data consistent with status
            practice = random.choice(practices) if status != "NEW" else None
            sa = random.choice(sa_list) if status in ["PENDING_ASSESSMENT", "UNDER_ASSESSMENT", "REVIEW_PENDING", "PENDING_GOVERNANCE", "COMPLETED_BID", "COMPLETED_NO_BID"] else None
            
            has_score = status in ["REVIEW_PENDING", "PENDING_GOVERNANCE", "COMPLETED_BID", "COMPLETED_NO_BID"]
            score = random.randint(70, 98) if has_score else 0
            
            rec = "APPROVED" if status in ["PENDING_GOVERNANCE", "COMPLETED_BID"] else ("REJECTED" if status == "COMPLETED_NO_BID" else None)
            decision = "GO" if status == "COMPLETED_BID" else ("NO_GO" if status == "COMPLETED_NO_BID" else None)

            opp = Opportunity(
                remote_id=f"CRM-{8000+i}",
                name=f"{customer} Strategic {practice or 'IT'} Project",
                customer=customer,
                deal_value=random.randint(500000, 10000000),
                currency="USD",
                win_probability=score,
                workflow_status=status,
                practice=practice,
                sa_owner=sa,
                sa_notes="High value opportunity with strategic alignment." if has_score else None,
                practice_head_recommendation=rec,
                management_decision=decision,
                close_reason="Market growth" if decision == "GO" else ("Low technical feasibility" if decision == "NO_GO" else None),
                last_synced_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            db.add(opp)
        
        db.commit()
        print(f"✓ Successfully seeded 25 opportunities across all workflow stages.")

        # 4. Create dummy assessments for the "History" or "Review" ones
        print("[4/4] Creating assessment records for submitted items...")
        submitted_opps = db.query(Opportunity).filter(Opportunity.workflow_status.in_(["REVIEW_PENDING", "PENDING_GOVERNANCE", "COMPLETED_BID", "COMPLETED_NO_BID"])).all()
        
        for opp in submitted_opps:
            assessment = Assessment(
                opp_id=opp.id,
                version="v1.0",
                scores={"technical": 8, "financial": 7, "strategic": 9},
                comments="Comprehensive assessment completed. Strong alignment with our core strengths.",
                risks=[{"category": "Delivery", "desc": "Aggressive timeline", "severity": "Medium"}],
                is_submitted=True,
                created_by=f"{opp.sa_owner.lower().replace(' ', '.')}@company.com" if opp.sa_owner else "system@company.com"
            )
            db.add(assessment)
        
        db.commit()
        print(f"✓ Created {len(submitted_opps)} detailed assessment records.")

        print("\n" + "="*60)
        print("✅ DATABASE POPULATED SUCCESSFULLY")
        print("="*60)

    except Exception as e:
        print(f"\n❌ POPULATION FAILED: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
