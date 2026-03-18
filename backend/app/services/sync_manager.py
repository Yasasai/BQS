
import os
import sys
import httpx
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Path: .../backend/app/services/sync_manager.py -> .../
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

from backend.app.services.oracle_service import ORACLE_REST_ROOT, ORACLE_USER, ORACLE_PASS, ORACLE_BASE_URL


from backend.app.core.logging_config import get_logger

logger = get_logger("sync_manager")

def log(msg): 
    logger.info(msg)


from backend.app.core.database import SessionLocal, init_db
from backend.app.models import Opportunity, Practice, AppUser, UserRole, Role

def map_oracle_to_db(item, db: Session):
    """Map Oracle JSON to our Opportunity model"""
    try:
        opty_id = str(item.get("OptyId"))
        if not opty_id: return None
        
        # Parse dates
        last_update_str = item.get("LastUpdateDate") or item.get("OptyLastUpdateDate")
        crm_last_updated_at = datetime.now(timezone.utc)
        if last_update_str:
            try:
                crm_last_updated_at = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
            except Exception as e: 
                pass
            
        close_date = None
        if item.get("EffectiveDate"):
            try:
                close_date = datetime.strptime(item["EffectiveDate"][:10], "%Y-%m-%d")
            except Exception as e: 
                pass

        # Practice lookup/create
        primary_practice_id = None
        practice_val = item.get("Practice_c")
        if practice_val:
            prac = db.query(Practice).filter(Practice.practice_name == practice_val).first()
            if not prac:
                try:
                    with db.begin_nested():
                        import uuid
                        import hashlib
                        prac_id = str(uuid.uuid4())
                        safe_code = practice_val.upper().replace(" ", "_")[:50]
                        hash_suffix = hashlib.md5(practice_val.encode('utf-8')).hexdigest()[:8]
                        prac = Practice(
                            practice_id=prac_id,
                            practice_code=f"{safe_code}_{hash_suffix}",
                            practice_name=practice_val[:255]
                        )
                        db.add(prac)
                        db.flush()
                except Exception as e:
                    # Ignore flush failure and continue without practice tracking this time,
                    # since DB rolled back to savepoint
                    prac = None
            if prac:
                primary_practice_id = prac.practice_id

        # Bid Manager Assignment MVP Logic
        bid_manager_id = None
        deal_value = float(item.get("Revenue") or 0)
        if deal_value > 0:
            sp_user = db.query(AppUser).join(UserRole).join(Role).filter(
                Role.role_code == 'SP',
                AppUser.is_active == True
            ).first()
            if sp_user:
                bid_manager_id = sp_user.user_id

        return {
            "opp_id": opty_id[:255],
            "opp_number": str(item.get("OptyNumber") or opty_id)[:255],
            "opp_name": (item.get("Name") or f"Opportunity {opty_id}")[:255],
            "customer_name": (item.get("TargetPartyName") or "Unknown Account")[:255],
            "geo": (item.get("GEO_c") or item.get("Geo_c") or item.get("Region_c") or "Unknown")[:255],
            "currency": str(item.get("CurrencyCode") or "USD")[:10],
            "deal_value": deal_value,
            "stage": (item.get("SalesStage") or "Qualification")[:255],
            "close_date": close_date,
            "crm_last_updated_at": crm_last_updated_at,
            "primary_practice_id": primary_practice_id,
            "workflow_status": item.get("WorkflowStatus") or "NEW",
            "bid_manager_user_id": bid_manager_id,
            "is_active": True
        }
    except Exception as e:
        log(f"⚠️ Mapping Error for {item.get('OptyId', 'Unknown')}: {e}")
        return None

def sync_opportunities():
    """
    Fetches ALL opportunities using RecordSet='ALL' with proper field names.
    """
    try:
        log("🚀 Starting CLEAN Dynamic Sync...")
        
        init_db()
        
        # 1. Base URL
        endpoint = f"{ORACLE_BASE_URL}/crmRestApi/resources/latest/opportunities"
        
        # 2. Batch settings - Process 50 records at a time
        limit = 50  # Batch size
        offset = 0
        total_saved = 0
        batch_number = 1
        has_more = True
        
        with httpx.Client(auth=(ORACLE_USER, ORACLE_PASS), timeout=60.0) as client:
            while has_more:
                db = SessionLocal()
                log(f"\n{'='*70}")
                log(f"📦 BATCH {batch_number}: Fetching records {offset} to {offset + limit - 1}")
                log(f"{'='*70}")
                
                # 3. USER'S EXACT URL FORMAT
                # Using MyOpportunitiesFinder with RecordSet='ALLOPTIES'
                url = (
                    f"{ORACLE_REST_ROOT}/opportunities"
                    f"?finder=MyOpportunitiesFinder;RecordSet='ALLOPTIES'"
                    f"&limit={limit}"
                    f"&offset={offset}"
                )
                
                # Log the EXACT URL being sent
                log(f"🔗 Requesting: {url}")
                
                try:
                    # 4. Make Request (NO params argument - URL is complete)
                    response = client.get(url)
                    
                    if response.status_code != 200:
                        log(f"❌ API Error: {response.status_code} - {response.text[:200]}")
                        break
                    
                    data = response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        log("✅ No more items found.")
                        has_more = False
                        break
                    
                    log(f"📝 Processing {len(items)} items in this batch...")
                    
                    # 5. Process each item
                    batch_saved = 0
                    for item in items:
                        mapped = map_oracle_to_db(item, db)
                        if not mapped:
                            continue
                        
                        try:
                            with db.begin_nested():
                                existing = db.query(Opportunity).filter(
                                    Opportunity.opp_id == mapped["opp_id"]
                                ).first()
                                
                                if existing:
                                    for k, v in mapped.items():
                                        if k == 'workflow_status' and existing.workflow_status:
                                            continue
                                        if k == 'bid_manager_user_id' and existing.bid_manager_user_id:
                                            continue
                                        setattr(existing, k, v)
                                else:
                                    db.add(Opportunity(**mapped))
                            
                            batch_saved += 1
                            total_saved += 1
                            logger.info(f"   ✓ Tracked: {mapped['opp_name'][:50]}")
                            
                        except Exception as e:
                            log(f"⚠️ DB Error: {e}")
                    
                    # Commit at the batch level
                    try:
                        db.commit()
                        log(f"✅ Batch {batch_number} complete: {batch_saved}/{len(items)} saved")
                        log(f"📊 Total saved so far: {total_saved}")
                    except Exception as e:
                        db.rollback()
                        log(f"❌ Batch commit failed: {e}")
                    
                    # 6. Pagination Check
                    if len(items) < limit:
                        has_more = False
                    else:
                        offset += limit
                        batch_number += 1
                    
                except Exception as e:
                    db.rollback() # clearing state to prevent InFailedSqlTransaction
                    log(f"💥 Request Error: {e}")
                    break
                finally:
                    db.close()
        
        log(f"🎉 Sync Complete! Total Saved: {total_saved} opportunities")
        logger.info(f"STAGE 5 SUCCESS: Extracted and passed records to database logic.")
        return total_saved
    except Exception as e:
        logger.error(f"STAGE 5 FATAL: Sync crashed with error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    sync_opportunities()
