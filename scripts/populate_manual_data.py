
import sys
import os
import re

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal, Opportunity, OpportunityDetails, init_db

# Data transcribed from the provided image
# Columns: Win(%), Opp Num, Name, Owner, Practice, Status, Creation Date, Account, AccountOwner, Amount, Est Billing, Sales Stage, Region
manual_data = [
    {
        "remote_id": "1602737",
        "name": "1569344 IAM one outsource 12m offshore",
        "win_probability": 100.0,
        "sales_owner": "Kamal AL Al Salloum",
        "practice": "IAM - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2024-01-23",
        "customer": "Beta Information Technology (Beta)",
        "amount_str": "270,002 SAR", # Inferring SAR from MEA - Saudi Arabia context and symbol style if ambiguous
        "deal_value": 270002.0,
        "currency": "SAR",
        "estimated_billing_date": "2024-02-12",
        "stage": "PO Received",
        "region": "MEA - Saudi Arabia"
    },
    {
        "remote_id": "1602738",
        "name": "1572704 STC12 Months",
        "win_probability": 100.0,
        "sales_owner": "Kamal AL Al Salloum",
        "practice": "Analytics - Digital",
        "status": "4. Commit",
        "creation_date": "2024-01-23",
        "customer": "SAS Middle East FZ-LLC (\"SAS\")",
        "amount_str": "252,000 SAR", # Assuming SAR based on owner match with above
        "deal_value": 252000.0,
        "currency": "SAR",
        "estimated_billing_date": "2024-02-12",
        "stage": "PO Received",
        "region": "MEA - Saudi Arabia"
    },
    {
        "remote_id": "1693827",
        "name": "1573697 revised IMR DDoS Yr 2 3",
        "win_probability": 100.0,
        "sales_owner": "Afzal Shaikh",
        "practice": "Infra & Cloud Security",
        "status": "4. Commit",
        "creation_date": "2024-08-02",
        "customer": "I&M Bank Rwanda Limited",
        "amount_str": "$65,700",
        "deal_value": 65700.0,
        "currency": "USD",
        "estimated_billing_date": "2024-08-29",
        "stage": "PO Received",
        "region": "MEA - Dubai"
    },
    {
        "remote_id": "1658743",
        "name": "2024 GRC outsource 12 months",
        "win_probability": 100.0,
        "sales_owner": "Kamal AL Al Salloum",
        "practice": "Advisory - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2024-06-10",
        "customer": "Tawuniya Cooperative Insurance",
        "amount_str": "2,004,012 SAR",
        "deal_value": 2004012.0,
        "currency": "SAR",
        "estimated_billing_date": "2024-06-11",
        "stage": "PO Received",
        "region": "MEA - Saudi Arabia"
    },
    {
        "remote_id": "1658758",
        "name": "2024 PAM Solution BNR",
        "win_probability": 100.0,
        "sales_owner": "Monish Mukherjee",
        "practice": "IAM - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2024-06-12",
        "customer": "National Bank of Rwanda",
        "amount_str": "$105,000",
        "deal_value": 105000.0,
        "currency": "USD",
        "estimated_billing_date": "2024-06-20",
        "stage": "PO Received",
        "region": "MEA - Kenya"
    },
    {
        "remote_id": "1657755",
        "name": "2024 SIEM 1800 servers",
        "win_probability": 100.0,
        "sales_owner": "pradeep augustin",
        "practice": "MSSP - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2024-06-08",
        "customer": "GT Bank",
        "amount_str": "$2,388,888",
        "deal_value": 2388888.0,
        "currency": "USD",
        "estimated_billing_date": "2024-06-07",
        "stage": "PO Received",
        "region": "MEA - Dubai"
    },
    {
        "remote_id": "1744044",
        "name": "2025 SIEM 1800 servers",
        "win_probability": 100.0,
        "sales_owner": "pradeep augustin",
        "practice": "MSSP - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2025-02-08",
        "customer": "GT Bank",
        "amount_str": "$2,388,888",
        "deal_value": 2388888.0,
        "currency": "USD",
        "estimated_billing_date": "2025-02-28",
        "stage": "PO Received",
        "region": "MEA - Dubai"
    },
    {
        "remote_id": "1754130",
        "name": "2025 SIEM 1800 servers Kenya rev1",
        "win_probability": 100.0,
        "sales_owner": "Afzal Shaikh",
        "practice": "MSSP - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2025-03-28",
        "customer": "GT Bank",
        "amount_str": "$70,340",
        "deal_value": 70340.0,
        "currency": "USD",
        "estimated_billing_date": "2025-03-31",
        "stage": "PO Received",
        "region": "MEA - Kenya"
    },
    {
        "remote_id": "1759271",
        "name": "2025 VAPT",
        "win_probability": 100.0,
        "sales_owner": "Pacifico Jr De Guzman",
        "practice": "TVM - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2025-05-29",
        "customer": "East West Ageas Life Insurance",
        "amount_str": "Php997,222",
        "deal_value": 997222.0,
        "currency": "PHP",
        "estimated_billing_date": "2025-06-27",
        "stage": "PO Received",
        "region": "ASEAN - Philippines"
    },
    {
        "remote_id": "1755209",
        "name": "2nd Threat Hunting HFCL",
        "win_probability": 100.0,
        "sales_owner": "Devansh Singh",
        "practice": "TVM - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2025-04-10",
        "customer": "HERO FINCORP LIMITED",
        "amount_str": "Rs1,801,050",
        "deal_value": 1801050.0,
        "currency": "INR",
        "estimated_billing_date": "2025-06-26",
        "stage": "PO Received",
        "region": "India - North"
    },
    {
        "remote_id": "1733846",
        "name": "2nd VAPT PO for Royal Enfield",
        "win_probability": 100.0,
        "sales_owner": "Devansh Singh",
        "practice": "TVM - Cybersecurity",
        "status": "4. Commit",
        "creation_date": "2024-12-13",
        "customer": "ROYAL ENFIELD (A UNIT OF EICHER MOTORS)",
        "amount_str": "Rs275,000",
        "deal_value": 275000.0,
        "currency": "INR",
        "estimated_billing_date": "2024-12-30",
        "stage": "Fully Billed",
        "region": "India - North"
    }
]

def populate_manual_data():
    db = SessionLocal()
    print("🚀 Starting manual data population...")
    
    for item in manual_data:
        try:
            # 1. Upsert Opportunity (Main Table)
            opp = db.query(Opportunity).filter(Opportunity.remote_id == item["remote_id"]).first()
            if not opp:
                opp = Opportunity(remote_id=item["remote_id"])
                db.add(opp)
            
            opp.name = item["name"]
            opp.win_probability = item["win_probability"]
            opp.sales_owner = item["sales_owner"]
            opp.practice = item["practice"]
            opp.customer = item["customer"]
            opp.deal_value = item["deal_value"]
            opp.currency = item["currency"]
            opp.estimated_billing_date = item["estimated_billing_date"]
            opp.stage = item["stage"]
            opp.geo = item["region"].split(" - ")[0] if " - " in item["region"] else item["region"]
            opp.region = item["region"]
            opp.workflow_status = "NEW_FROM_CRM"
            
            # 2. Upsert OpportunityDetails (Detailed Table)
            detail = db.query(OpportunityDetails).filter(OpportunityDetails.opty_number == item["remote_id"]).first()
            if not detail:
                detail = OpportunityDetails(opty_number=item["remote_id"])
                db.add(detail)
            
            detail.name = item["name"]
            detail.win_probability = item["win_probability"]
            detail.owner_name = item["sales_owner"]
            detail.practice = item["practice"]
            detail.account_name = item["customer"]
            detail.revenue = item["deal_value"]
            detail.currency_code = item["currency"]
            detail.effective_date = item["estimated_billing_date"]
            detail.sales_stage = item["stage"]
            detail.geo = opp.geo
            detail.region = opp.region
            detail.status_label = item["status"]
            detail.creation_date = item["creation_date"]
            
            print(f"✅ Upserted: {item['remote_id']} - {item['name']}")
            
        except Exception as e:
            print(f"❌ Error processing {item.get('remote_id', 'Unknown')}: {e}")
            db.rollback()
            continue
            
    db.commit()
    db.close()
    print("✨ Manual population complete!")

if __name__ == "__main__":
    populate_manual_data()
