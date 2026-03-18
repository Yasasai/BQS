import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models import CRMOpportunity, CRMOpportunityResource, CRMSyncRun

logger = logging.getLogger(__name__)

def generate_hash(payload: Dict[str, Any]) -> str:
    """
    Generate a deterministic SHA256 hash of the payload for change detection.
    """
    # Ensure keys are sorted for determinism and handle non-serializable objects
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

def parse_oracle_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Helper to parse Oracle ISO date strings safely.
    """
    if not date_str:
        return None
    try:
        # Handle Zulu suffix and offsets
        cleaned = date_str.replace('Z', '+00:00')
        return datetime.fromisoformat(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Failed to parse date string: {date_str}")
        return None

def process_opportunities(session: Session, opportunities: List[Dict[str, Any]], sync_run_id: str) -> int:
    """
    Task 1: Opportunity Upsert Logic (Stage C)
    Idempotent logic to sync Oracle opportunities into the local operational replica.
    Returns the count of new or changed opportunities.
    """
    upsert_count = 0
    for opty_data in opportunities:
        opty_id = str(opty_data.get('OptyId'))
        if not opty_id:
            logger.error("Skipping opportunity with missing OptyId")
            continue

        source_hash = generate_hash(opty_data)
        now = datetime.now(timezone.utc)
        
        # Check for existing record
        existing = session.query(CRMOpportunity).filter(CRMOpportunity.opty_id == opty_id).first()
        
        db_hash = existing.source_hash if existing else "NONE"
        logger.debug(f"Processing OptyId: {opty_id}")
        logger.debug(f"OptyId {opty_id} found in DB: {bool(existing)} | DB Hash: {db_hash} | Oracle Hash: {source_hash}")
        
        if not existing:
            # Case: New Opportunity
            new_opty = CRMOpportunity(
                opty_id=opty_id,
                opty_number=opty_data.get('OptyNumber'),
                source_hash=source_hash,
                source_payload_json=opty_data,
                last_seen_ts=now,
                last_synced_run_id=sync_run_id,
                
                name=opty_data.get('Name', 'Unknown'),
                revenue=opty_data.get('Revenue'),
                currency=opty_data.get('CurrencyCode'),
                stage=opty_data.get('SalesStage'),
                close_date=parse_oracle_date(opty_data.get('CloseDate')),
                customer_name=opty_data.get('TargetPartyName') or opty_data.get('AccountName'),
                owner_email=opty_data.get('OwnerEmailAddress'),
                
                enrichment_status='PENDING' # Mark for Stage D
            )
            session.add(new_opty)
            upsert_count += 1
            logger.info("ACTION: INSERTING new record")
            logger.info(f"Inserted new opportunity: {opty_id}")
        
        elif existing.source_hash != source_hash:
            # Case: Hash changed - Update everything
            existing.source_payload_json = opty_data
            existing.source_hash = source_hash
            existing.last_seen_ts = now
            existing.last_synced_run_id = sync_run_id
            
            # Update fields
            existing.name = opty_data.get('Name', existing.name)
            existing.revenue = opty_data.get('Revenue')
            existing.currency = opty_data.get('CurrencyCode')
            existing.stage = opty_data.get('SalesStage')
            existing.close_date = parse_oracle_date(opty_data.get('CloseDate'))
            existing.customer_name = opty_data.get('TargetPartyName') or opty_data.get('AccountName')
            existing.owner_email = opty_data.get('OwnerEmailAddress')
            
            # Re-flag for enrichment
            existing.enrichment_status = 'PENDING'
            upsert_count += 1
            logger.info("ACTION: UPDATING existing record")
            logger.info(f"Updated changed opportunity: {opty_id}")
            
        else:
            # Case: No change - Only update bookkeeping timestamps
            existing.last_seen_ts = now
            existing.last_synced_run_id = sync_run_id
            logger.info("ACTION: SKIPPING identical record")
            logger.debug(f"No changes for opportunity: {opty_id}")
    
    return upsert_count

def identify_enrichment_targets(session: Session, forced_refresh_hours: int = 24) -> List[CRMOpportunity]:
    """
    Task 2: Identify Enrichment Targets (Stage D)
    Detects which opportunities require detailed resource data fetching.
    Flags opportunities based on business rules and returns the list.
    """
    refresh_threshold = datetime.now(timezone.utc) - timedelta(hours=forced_refresh_hours)
    
    # Subquery to find opportunities that already have active resources
    resource_subq = session.query(CRMOpportunityResource.opty_id).filter(
        CRMOpportunityResource.is_active == True
    ).distinct().subquery()

    # Query matching requirements:
    # 1. enrichment_status is PENDING (New or hash changed)
    # 2. enrichment_status is FAILED (Retry previous failures)
    # 3. No active resources found in local DB
    # 4. last_enriched_at is older than the forced refresh window
    # 5. last_enriched_at is NULL (Never enriched)
    targets = session.query(CRMOpportunity).filter(
        (CRMOpportunity.enrichment_status == 'PENDING') |
        (CRMOpportunity.enrichment_status == 'FAILED') |
        (~CRMOpportunity.opty_id.in_(resource_subq)) |
        (CRMOpportunity.last_enriched_at < refresh_threshold) |
        (CRMOpportunity.last_enriched_at == None)
    ).all()

    # Mark as PENDING if not already
    for target in targets:
        if target.enrichment_status not in ['PENDING', 'FAILED']:
            target.enrichment_status = 'PENDING'
            
    return targets

def process_resources(session: Session, opty_id: str, opty_number: str, resources: List[Dict[str, Any]], sync_run_id: str) -> int:
    """
    Task 3: Resource Upsert & Soft-Deactivate (Stage F)
    Syncs team members for a specific opportunity.
    Returns the count of new/updated resource rows.
    """
    # 1. Map incoming resources by email
    incoming_map = {}
    upsert_count = 0
    for res_data in resources:
        email = res_data.get('EmailAddress')
        if email:
            incoming_map[email.lower()] = res_data

    # 2. Fetch existing local resources for this opportunity
    existing_resources = session.query(CRMOpportunityResource).filter(
        CRMOpportunityResource.opty_id == opty_id
    ).all()
    
    now = datetime.now(timezone.utc)

    # 3. Upsert Logic
    for email, res_data in incoming_map.items():
        res_hash = generate_hash(res_data)
        
        # Check if we have this resource locally
        local_res = next((r for r in existing_resources if r.email.lower() == email), None)

        if not local_res:
            # INSERT
            new_res = CRMOpportunityResource(
                opty_id=opty_id,
                opty_number=opty_number,
                email=email,
                name=res_data.get('MemberName') or res_data.get('Name'),
                role_name=res_data.get('ResourceRoleName') or res_data.get('RoleName'),
                source_hash=res_hash,
                last_seen_ts=now,
                last_synced_run_id=sync_run_id,
                is_active=True
            )
            session.add(new_res)
            upsert_count += 1
        else:
            # UPDATE (If hash changed or it was inactive)
            if local_res.source_hash != res_hash or not local_res.is_active:
                local_res.name = res_data.get('MemberName') or res_data.get('Name')
                local_res.role_name = res_data.get('ResourceRoleName') or res_data.get('RoleName')
                local_res.source_hash = res_hash
                local_res.is_active = True # Reactivate if it was soft-deleted
                local_res.last_seen_ts = now
                local_res.last_synced_run_id = sync_run_id
                upsert_count += 1
            else:
                # Still active and no change, just heartbeat timestamps
                local_res.last_seen_ts = now
                local_res.last_synced_run_id = sync_run_id

    # 4. Soft-Deactivate Logic
    # If a resource was previously local but NOT returned by Oracle this time
    for local_res in existing_resources:
        if local_res.email.lower() not in incoming_map:
            if local_res.is_active:
                logger.info(f"Soft-deactivating resource {local_res.email} for opty {opty_id}")
                local_res.is_active = False
                # Per requirements: "leaving the last_seen_ts unchanged"
                local_res.last_synced_run_id = sync_run_id

    # Update opportunity enrichment status to mark success for this stage
    opty = session.query(CRMOpportunity).filter(CRMOpportunity.opty_id == opty_id).first()
    if opty:
        opty.enrichment_status = 'COMPLETED'
        opty.last_enriched_at = now
    
    return upsert_count
