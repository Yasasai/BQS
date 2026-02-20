"""
Migration script to update existing opportunities with proper workflow states.
This ensures all 962 opportunities have correct initial states.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from app.models import Opportunity

def migrate_workflow_states():
    """Update all opportunities to have proper workflow states"""
    
    db = SessionLocal()
    
    try:
        print("🔄 Starting workflow state migration...")
        print("=" * 60)
        
        # Get all opportunities
        opportunities = db.query(Opportunity).all()
        total = len(opportunities)
        print(f"📊 Found {total} opportunities to process\n")
        
        # Counters
        updated_to_new = 0
        updated_to_heads_assigned = 0
        updated_to_executors_assigned = 0
        already_correct = 0
        
        for opp in opportunities:
            old_status = opp.workflow_status
            
            # Determine correct state based on assignments
            if opp.assigned_sa_id and opp.assigned_sp_id:
                # Both SA and SP assigned
                if opp.workflow_status not in ['IN_ASSESSMENT', 'UNDER_REVIEW', 'APPROVED', 'REJECTED']:
                    opp.workflow_status = 'EXECUTORS_ASSIGNED'
                    updated_to_executors_assigned += 1
                else:
                    already_correct += 1
                    
            elif opp.assigned_practice_head_id and opp.assigned_sales_head_id:
                # Both PH and SH assigned but not SA/SP
                if opp.workflow_status not in ['HEADS_ASSIGNED', 'EXECUTORS_ASSIGNED', 'IN_ASSESSMENT', 'UNDER_REVIEW', 'APPROVED', 'REJECTED']:
                    opp.workflow_status = 'HEADS_ASSIGNED'
                    updated_to_heads_assigned += 1
                else:
                    already_correct += 1
                    
            else:
                # No assignments or partial assignments
                if opp.workflow_status in [None, '', 'OPEN']:
                    opp.workflow_status = 'NEW'
                    updated_to_new += 1
                elif opp.workflow_status in ['APPROVED', 'REJECTED', 'IN_ASSESSMENT', 'UNDER_REVIEW']:
                    already_correct += 1
                else:
                    # Legacy states, reset to NEW
                    opp.workflow_status = 'NEW'
                    updated_to_new += 1
            
            # Ensure approval statuses are set
            if not opp.gh_approval_status:
                opp.gh_approval_status = 'PENDING'
            if not opp.ph_approval_status:
                opp.ph_approval_status = 'PENDING'
            if not opp.sh_approval_status:
                opp.sh_approval_status = 'PENDING'
        
        # Commit all changes
        db.commit()
        
        print("\n📊 Migration Summary:")
        print("=" * 60)
        print(f"  Updated to NEW:                {updated_to_new:4d}")
        print(f"  Updated to HEADS_ASSIGNED:     {updated_to_heads_assigned:4d}")
        print(f"  Updated to EXECUTORS_ASSIGNED: {updated_to_executors_assigned:4d}")
        print(f"  Already correct:               {already_correct:4d}")
        print(f"  {'─' * 58}")
        print(f"  Total processed:               {total:4d}")
        print("=" * 60)
        
        # Show state distribution
        print("\n📈 Current State Distribution:")
        print("=" * 60)
        from sqlalchemy import func
        state_counts = db.query(
            Opportunity.workflow_status,
            func.count(Opportunity.opp_id).label('count')
        ).group_by(Opportunity.workflow_status).all()
        
        for state, count in sorted(state_counts, key=lambda x: x[1], reverse=True):
            state_display = state if state else '(null)'
            print(f"  {state_display:25s} : {count:4d}")
        print("=" * 60)
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_workflow_states()
