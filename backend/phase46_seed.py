# -*- coding: utf-8 -*-
"""
Phase 4.6 - Pure psycopg2 Opportunity Seeder
=============================================
No SQLAlchemy import chain - connects directly to PostgreSQL.

Run from the backend folder:
    python phase46_seed.py
"""
import psycopg2
import uuid
import random
from datetime import datetime, timedelta

# ─── Config ────────────────────────────────────────────────────────────────
DB = dict(dbname="bqs", user="postgres", password="Abcd1234",
          host="127.0.0.1", port=5432)

# ─── Static Data ───────────────────────────────────────────────────────────
CUSTOMERS = [
    "JPMorgan Chase","FedEx Logistics","Coca-Cola Enterprises",
    "Tesla Energy","Apple EMEA","Google Cloud","Amazon Web Services",
    "Netflix Studios","Microsoft Azure","Samsung Electronics",
    "HSBC Banking","Siemens AG","Oracle Corp","SAP SE","Accenture",
    "Deloitte Advisory","Goldman Sachs","UnitedHealth Group","Pfizer Ltd","Boeing"
]
GEO_LIST  = ["APAC", "EMEA", "NAMER", "LATAM", "MEA"]
STAGES    = ["1. Prospect","2. Develop","3. Qualify","4. Commit","5. Closed Won"]
PRACTICE_DATA = [
    ("CLOUD", "Cloud & Infrastructure"),
    ("CYBER", "Cybersecurity"),
    ("DATA",  "Data & Analytics"),
    ("AI_ML", "AI & Machine Learning"),
    ("ERP",   "Enterprise ERP"),
    ("NET",   "Networking"),
    ("SOFT",  "Software Engineering"),
]
WORKFLOW_STATUSES = [
    "NEW_FROM_CRM",
    "ASSIGNED_TO_SA",
    "UNDER_ASSESSMENT",
    "WAITING_PH_APPROVAL",
    "READY_FOR_MGMT_REVIEW",
    "APPROVED",
    "REJECTED",
]

def ts(days_ago=0):
    return datetime.utcnow() - timedelta(days=days_ago)

def future(days=90):
    return datetime.utcnow() + timedelta(days=random.randint(30, days))

def upsert_practice(cur, code, name):
    cur.execute("SELECT practice_id FROM practice WHERE practice_name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    pid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO practice (practice_id, practice_code, practice_name) VALUES (%s,%s,%s)",
        (pid, code[:20], name)
    )
    return pid

def get_users_by_role(cur, role_code):
    cur.execute("""
        SELECT au.user_id FROM app_user au
        JOIN user_role ur ON ur.user_id = au.user_id
        JOIN role r ON r.role_id = ur.role_id
        WHERE r.role_code = %s AND au.is_active = TRUE
    """, (role_code,))
    return [r[0] for r in cur.fetchall()]

def main():
    print("=" * 65)
    print("  BQS Phase 4.6 – Opportunity Seeder (psycopg2)")
    print("=" * 65)

    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur  = conn.cursor()

    try:
        # 0. Check current opportunity count
        cur.execute("SELECT COUNT(*) FROM opportunity")
        existing = cur.fetchone()[0]
        print(f"\n  Existing opportunities: {existing}")
        if existing >= 30:
            print("  ✅ Already have ≥30 opportunities. Nothing to do.")
            print("     (Truncate the opportunity table to re-seed.)")
            return

        # 1. Ensure practices
        print("\n[1/4] Upserting practice rows...")
        practice_map = {}
        for code, name in PRACTICE_DATA:
            pid = upsert_practice(cur, code, name)
            practice_map[name] = pid
            print(f"       {name}")
        conn.commit()

        # 2. Fetch user IDs by role
        print("\n[2/4] Fetching user IDs...")
        users = {rc: get_users_by_role(cur, rc)
                 for rc in ["GH","PH","SH","SA","SP"]}
        for rc, lst in users.items():
            print(f"       {rc}: {len(lst)} users")

        if not users["SH"] and not users["GH"]:
            print("  ⚠  No seeded users found – run seed_users.py first!")
            return

        # 3. Insert 30 opportunities
        print("\n[3/4] Inserting 30 opportunities...")
        status_pool = WORKFLOW_STATUSES * 5
        random.shuffle(status_pool)
        status_pool = status_pool[:30]

        inserted = 0
        for i, wf_status in enumerate(status_pool):
            customer    = CUSTOMERS[i % len(CUSTOMERS)]
            geo         = random.choice(GEO_LIST)
            prac_name   = random.choice(PRACTICE_DATA)[1]
            prac_id     = practice_map[prac_name]
            stage       = random.choice(STAGES)
            deal_value  = round(random.uniform(500_000, 15_000_000), 2)
            crm_ts      = ts(days_ago=random.randint(1, 90))
            close_dt    = future(200)

            sh_id = random.choice(users["SH"]) if users["SH"] else None
            sa_id = (random.choice(users["SA"]) if users["SA"]
                     and wf_status != "NEW_FROM_CRM" else None)
            ph_id = (random.choice(users["PH"]) if users["PH"]
                     and wf_status in ("WAITING_PH_APPROVAL","READY_FOR_MGMT_REVIEW",
                                        "APPROVED","REJECTED") else None)

            gh_ap = "APPROVED" if wf_status=="APPROVED" else (
                    "REJECTED" if wf_status=="REJECTED" else "PENDING")
            ph_ap = "APPROVED" if wf_status in ("READY_FOR_MGMT_REVIEW","APPROVED") else (
                    "REJECTED" if wf_status=="REJECTED" else "PENDING")
            sh_ap = "APPROVED" if wf_status in ("READY_FOR_MGMT_REVIEW","APPROVED") else "PENDING"
            sub_ready = wf_status in ("READY_FOR_MGMT_REVIEW","APPROVED","REJECTED")

            cur.execute("""
                INSERT INTO opportunity (
                    opp_id, opp_number, opp_name, customer_name, geo,
                    currency, deal_value, stage, close_date,
                    crm_last_updated_at, local_last_synced_at,
                    workflow_status, is_active,
                    primary_practice_id,
                    assigned_sales_head_id, assigned_sa_id,
                    assigned_practice_head_id,
                    gh_approval_status, ph_approval_status, sh_approval_status,
                    combined_submission_ready
                ) VALUES (
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,
                    %s,%s,
                    %s,
                    %s,%s,
                    %s,
                    %s,%s,%s,
                    %s
                )
                ON CONFLICT (opp_id) DO NOTHING
            """, (
                f"SEED-{1000+i}", f"BQS-{2024100+i}",
                f"{customer} {prac_name} Initiative",
                customer, geo,
                "USD", deal_value, stage, close_dt,
                crm_ts, datetime.utcnow(),
                wf_status, True,
                prac_id,
                sh_id, sa_id,
                ph_id,
                gh_ap, ph_ap, sh_ap,
                sub_ready
            ))
            inserted += 1

        conn.commit()
        print(f"  ✅  Inserted {inserted} opportunities.")

        # 4. Add score versions for scored statuses
        print("\n[4/4] Adding score versions...")
        cur.execute("""
            SELECT opp_id, assigned_sa_id, workflow_status
            FROM opportunity
            WHERE workflow_status IN (
                'UNDER_ASSESSMENT','WAITING_PH_APPROVAL',
                'READY_FOR_MGMT_REVIEW','APPROVED','REJECTED'
            )
            LIMIT 20
        """)
        scorable = cur.fetchall()

        # Check if scoring tables exist
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'opp_score_version'
            )
        """)
        scoring_exists = cur.fetchone()[0]

        if scoring_exists and scorable:
            # fetch sections
            cur.execute("SELECT section_code FROM opp_score_section")
            sections = [r[0] for r in cur.fetchall()]

            for opp_id, sa_id, wf_status in scorable:
                # Check if version already exists
                cur.execute(
                    "SELECT 1 FROM opp_score_version WHERE opp_id = %s", (opp_id,)
                )
                if cur.fetchone():
                    continue

                ver_id = str(uuid.uuid4())
                is_submitted = wf_status in (
                    "WAITING_PH_APPROVAL","READY_FOR_MGMT_REVIEW","APPROVED","REJECTED")
                cur.execute("""
                    INSERT INTO opp_score_version (
                        score_version_id, opp_id, version_no, status,
                        overall_score, confidence_level, recommendation,
                        summary_comment, created_by_user_id,
                        sa_submitted, sp_submitted, created_at, submitted_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    ver_id, opp_id, 1,
                    "SUBMITTED" if is_submitted else "DRAFT",
                    random.randint(55, 95),
                    random.choice(["High","Medium","Low"]),
                    random.choice(["BID","NO_BID","CONDITIONAL"]),
                    "Strong opportunity aligned with our portfolio.",
                    sa_id or (users["SA"][0] if users["SA"] else None),
                    True, True,
                    ts(days_ago=random.randint(5,30)),
                    ts(days_ago=random.randint(1,5)) if is_submitted else None
                ))

                for sec_code in sections:
                    cur.execute("""
                        INSERT INTO opp_score_values (
                            score_value_id, score_version_id, section_code,
                            score, notes, selected_reasons
                        ) VALUES (%s,%s,%s,%s,%s,%s)
                    """, (
                        str(uuid.uuid4()), ver_id, sec_code,
                        round(random.uniform(2.0, 5.0), 1),
                        "Assessment notes.", "[]"
                    ))
            conn.commit()
            print(f"  ✅  Score versions created for {len(scorable)} opportunities.")
        else:
            print("  ℹ  No scoring sections found or table missing, skipping scores.")

        # Summary
        cur.execute("SELECT COUNT(*) FROM opportunity")
        total = cur.fetchone()[0]
        cur.execute("""
            SELECT workflow_status, COUNT(*) FROM opportunity
            GROUP BY workflow_status ORDER BY workflow_status
        """)
        rows = cur.fetchall()
        print(f"\n{'='*65}")
        print(f"  TOTAL OPPORTUNITIES: {total}")
        print(f"  Status Breakdown:")
        for status, cnt in rows:
            print(f"    {(status or 'NULL'):<32} : {cnt}")
        print(f"{'='*65}")
        print("\n🚀 Done! All dashboards should now display data.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
