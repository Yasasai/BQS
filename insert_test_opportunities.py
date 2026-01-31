"""
Insert test opportunities into PostgreSQL database
Run this from the BQS root directory: python insert_test_opportunities.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Opportunity

# Database connection
DATABASE_URL = "postgresql://postgres:Abcd1234@127.0.0.1:5432/bqs"

print("=" * 60)
print("Inserting Test Opportunities")
print("=" * 60)

try:
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test opportunities
    test_opportunities = [
        {
            'opp_id': 'TEST-OPP-001',
            'opp_number': 'OPP-2024-001',
            'opp_name': 'Cloud Migration for Acme Corp',
            'customer_name': 'Acme Corporation',
            'deal_value': 500000,
            'currency': 'USD',
            'stage': 'Qualification',
            'geo': 'North America',
            'close_date': datetime.now() + timedelta(days=90),
            'crm_last_updated_at': datetime.now(),
            'workflow_status': None,  # Unassigned
            'is_active': True
        },
        {
            'opp_id': 'TEST-OPP-002',
            'opp_number': 'OPP-2024-002',
            'opp_name': 'ERP Implementation - Global Tech',
            'customer_name': 'Global Tech Solutions',
            'deal_value': 750000,
            'currency': 'USD',
            'stage': 'Proposal',
            'geo': 'EMEA',
            'close_date': datetime.now() + timedelta(days=120),
            'crm_last_updated_at': datetime.now(),
            'workflow_status': None,  # Unassigned
            'is_active': True
        },
        {
            'opp_id': 'TEST-OPP-003',
            'opp_number': 'OPP-2024-003',
            'opp_name': 'Data Analytics Platform - RetailCo',
            'customer_name': 'RetailCo International',
            'deal_value': 300000,
            'currency': 'EUR',
            'stage': 'Discovery',
            'geo': 'APAC',
            'close_date': datetime.now() + timedelta(days=150),
            'crm_last_updated_at': datetime.now(),
            'workflow_status': None,  # Unassigned
            'is_active': True
        }
    ]
    
    inserted_count = 0
    skipped_count = 0
    
    for opp_data in test_opportunities:
        # Check if already exists
        existing = session.query(Opportunity).filter(
            Opportunity.opp_id == opp_data['opp_id']
        ).first()
        
        if existing:
            print(f"⏭️  Skipped: {opp_data['opp_name']} (already exists)")
            skipped_count += 1
        else:
            new_opp = Opportunity(**opp_data)
            session.add(new_opp)
            print(f"✅ Inserted: {opp_data['opp_name']}")
            inserted_count += 1
    
    # Commit changes
    session.commit()
    
    print("\n" + "=" * 60)
    print(f"✅ Success!")
    print(f"   Inserted: {inserted_count} opportunities")
    print(f"   Skipped: {skipped_count} (already existed)")
    print("=" * 60)
    
    # Verify
    print("\n📊 Current opportunities in database:")
    all_opps = session.query(Opportunity).filter(Opportunity.is_active == True).all()
    print(f"   Total active opportunities: {len(all_opps)}")
    
    # Show test opportunities
    test_opps = session.query(Opportunity).filter(
        Opportunity.opp_id.like('TEST-OPP-%')
    ).all()
    
    if test_opps:
        print("\n🧪 Test opportunities:")
        for opp in test_opps:
            status = opp.workflow_status or 'UNASSIGNED'
            print(f"   - {opp.opp_name} ({status})")
    
    session.close()
    
    print("\n✅ Done! Refresh your frontend to see the opportunities.")
    print("   Go to: http://localhost:5176")
    print("   Navigate to: Practice Head Dashboard → Unassigned tab")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
