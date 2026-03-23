from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func, cast, String
from typing import List, Optional, Any
from datetime import datetime
import json
from backend.app.models import Opportunity, OpportunityAssignment, OppScoreVersion, Practice, AppUser, OppScoreSectionValue
from backend.app.core.logging_config import get_logger

logger = get_logger("opportunity_service")

def gname(db: Session, uid: Any):
    if not uid: return None
    if isinstance(uid, list):
        if not uid: return "N/A"
        users = db.query(AppUser).filter(AppUser.user_id.in_(uid)).all()
        # Maintain order if possible? Or just join
        names = [u.display_name for u in users]
        return ", ".join(names) if names else "N/A"
    u = db.query(AppUser).filter(AppUser.user_id == uid).first()
    return u.display_name if u else uid

def get_paginated_opportunities_logic(
    db: Session,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    tab: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    region: Optional[str] = None,
    filters: Optional[str] = None,
    current_user_email: Optional[str] = None
):
    skip = (page - 1) * limit
    
    # Base Query
    query = db.query(Opportunity).filter(Opportunity.is_active == True)
    query = query.outerjoin(AppUser, Opportunity.sales_owner_user_id == AppUser.user_id)
    query = query.outerjoin(Practice, Opportunity.primary_practice_id == Practice.practice_id)

    # Search
    if search:
        st = f"%{search}%"
        query = query.filter(or_(
            Opportunity.opp_name.ilike(st),
            Opportunity.customer_name.ilike(st),
            Opportunity.opp_number.ilike(st)
        ))

    # Region Filter
    if region and region != 'All Regions':
        query = query.filter(Opportunity.geo == region)

    # Column Filters
    if filters:
        try:
            filter_list = json.loads(filters)
            # Check if we need to join for win_probability
            has_win_prob = any(f.get('id') == 'win_probability' for f in filter_list)
            if has_win_prob:
                latest_score_subq = db.query(
                    OppScoreVersion.opp_id,
                    func.max(OppScoreVersion.version_no).label('max_version')
                ).group_by(OppScoreVersion.opp_id).subquery()
                
                query = query.outerjoin(
                    OppScoreVersion,
                    and_(
                        Opportunity.opp_id == OppScoreVersion.opp_id,
                        OppScoreVersion.version_no == latest_score_subq.c.max_version
                    )
                )

            for f in filter_list:
                col = f.get('id')
                val = f.get('value')
                if val is None: continue
                
                if isinstance(val, list):
                    if len(val) == 0: continue
                    if col == 'workflow_status':
                        query = query.filter(Opportunity.workflow_status.in_(val))
                    elif col == 'geo':
                        query = query.filter(Opportunity.geo.in_(val))
                    elif col == 'sales_stage':
                        query = query.filter(Opportunity.stage.in_(val))
                    elif col == 'account_owner' or col == 'owner':
                        query = query.filter(Opportunity.sales_owner_user_id.in_(val))
                elif isinstance(val, dict):
                    if col in ['deal_value', 'Amount']:
                        vmin = val.get('min'); vmax = val.get('max')
                        if vmin is not None and vmin != '': query = query.filter(Opportunity.deal_value >= float(vmin))
                        if vmax is not None and vmax != '': query = query.filter(Opportunity.deal_value <= float(vmax))
                    elif col == 'win_probability':
                        vmin = val.get('min'); vmax = val.get('max')
                        if vmin is not None and vmin != '': query = query.filter(OppScoreVersion.overall_score >= float(vmin))
                        if vmax is not None and vmax != '': query = query.filter(OppScoreVersion.overall_score <= float(vmax))
                else:
                    if col in ['customer', 'Account']:
                        query = query.filter(Opportunity.customer_name.ilike(f"%{val}%"))
                    elif col == 'practice':
                        query = query.join(Practice, Opportunity.primary_practice_id == Practice.practice_id) \
                                     .filter(Practice.practice_name.ilike(f"%{val}%"))
                    elif col in ['owner', 'account_owner']:
                        query = query.filter(Opportunity.sales_owner_user_id == val)
                    elif col == 'remote_id':
                        query = query.filter(Opportunity.opp_number.ilike(f"%{val}%"))
                    elif col == 'name' or col == 'opportunity_name':
                        query = query.filter(Opportunity.opportunity_name.ilike(f"%{val}%"))
        except Exception as e:
            logger.error(f"Filter error in service: {e}")

    # Role/Target filtering + Hierarchy Visibility
    hierarchy_filter = (AppUser.manager_email == current_user_email) if current_user_email else False
    
    if role in ('GH', 'ADMIN'):
        pass  # Full visibility — no user-scoping filter
    elif role == 'BM':
        query = query.filter(
            Opportunity.bid_manager_user_id == user_id
        ) if user_id else query.filter(False)
    elif role == 'PH':
        query = query.filter(or_(
            cast(Opportunity.assigned_practice_head_ids, String).like(f'%"{user_id}"%'),
            hierarchy_filter
        )) if user_id else query.filter(False)
    elif role == 'SH':
        query = query.filter(or_(
            Opportunity.assigned_sales_head_id == user_id,
            hierarchy_filter
        )) if user_id else query.filter(False)
    elif role == 'SA':
        query = query.filter(or_(
            cast(Opportunity.assigned_sa_ids, String).like(f'%"{user_id}"%'),
            hierarchy_filter
        )) if user_id else query.filter(False)
    elif role == 'SP':
        query = query.filter(or_(
            Opportunity.assigned_sp_id == user_id,
            hierarchy_filter
        )) if user_id else query.filter(False)
    elif role in ('LEGAL', 'LL'):
        query = query.filter(or_(
            Opportunity.assigned_legal_id == user_id,
            hierarchy_filter
        )) if user_id else query.filter(False)
    elif role == 'FINANCE':
        query = query.filter(or_(
            Opportunity.assigned_finance_id == user_id,
            hierarchy_filter
        )) if user_id else query.filter(False)

    # Tab filtering
    rev_stats = ['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']
    comp_stats = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']

    tabs = tab.split(",") if tab else ["all"]
    tab_filters = []
    for t in tabs:
        if t == 'all': tab_filters.append(True)
        elif t == 'closed':
            tab_filters.append(Opportunity.workflow_status == 'CLOSED')
        elif t == 'current-assignments':
            # BM active work: assigned and not CLOSED
            tab_filters.append(and_(
                Opportunity.bid_manager_user_id == user_id,
                Opportunity.workflow_status.notin_(['CLOSED'])
            ))
        elif t in ['review', 'pending-review', 'submitted']:
            tab_filters.append(Opportunity.workflow_status.in_(rev_stats))
        elif t == 'completed':
            if role == 'PH': tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED'])))
            elif role == 'SH': tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED'])))
            elif role == 'GH': tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.gh_approval_status.in_(['APPROVED', 'REJECTED'])))
            elif role == 'SA': tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SA_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED'])))
            elif role == 'SP': tab_filters.append(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_(['SP_SUBMITTED', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED'])))
            else: tab_filters.append(Opportunity.workflow_status.in_(comp_stats))
        elif t == 'missing-ph' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.isnot(None)))
        elif t == 'missing-sh' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sales_head_id.is_(None), and_(Opportunity.assigned_practice_head_ids != None, cast(Opportunity.assigned_practice_head_ids, String) != '[]')))
        elif t == 'fully-assigned' and role == 'GH':
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_practice_head_ids != None, cast(Opportunity.assigned_practice_head_ids, String) != '[]', Opportunity.assigned_sales_head_id.isnot(None)))
        elif t == 'partially-assigned' and role == 'GH':
            cond = or_(
                and_(or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.isnot(None)),
                and_(Opportunity.assigned_practice_head_ids != None, cast(Opportunity.assigned_practice_head_ids, String) != '[]', Opportunity.assigned_sales_head_id.is_(None))
            )
            tab_filters.append(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), cond))
        elif t in ['action-required', 'unassigned', 'needs-action']:
            tf = (or_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.is_(None)))
            if role == 'PH': tf = and_(tf, or_(Opportunity.assigned_sa_ids == None, cast(Opportunity.assigned_sa_ids, String) == '[]'))
            elif role == 'SH': tf = and_(tf, Opportunity.assigned_sp_id.is_(None))
            elif role == 'GH':
                if t == 'unassigned': tf = and_(tf, or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.is_(None))
                else: tf = and_(tf, or_(or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.is_(None)))
            elif role in ['SA', 'SP']:
                tf = and_(tf, or_(Opportunity.workflow_status.notin_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT'] + rev_stats + comp_stats), Opportunity.workflow_status.is_(None)))
            tab_filters.append(tf)
        elif t == 'in-progress':
            tf = (or_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.is_(None)))
            if role == 'PH': tf = and_(tf, Opportunity.assigned_sa_ids != None, cast(Opportunity.assigned_sa_ids, String) != '[]')
            elif role == 'SH': tf = and_(tf, Opportunity.assigned_sp_id.isnot(None))
            elif role in ['SA', 'SP']: tf = and_(tf, Opportunity.workflow_status.in_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT']))
            else: tf = and_(tf, or_(and_(Opportunity.assigned_practice_head_ids != None, cast(Opportunity.assigned_practice_head_ids, String) != '[]'), Opportunity.assigned_sales_head_id.isnot(None)))
            tab_filters.append(tf)

    if tab_filters:
        query = query.filter(or_(*tab_filters))

    total_count = query.count()
    pipeline_value = db.query(func.sum(Opportunity.deal_value)).filter(Opportunity.opp_id.in_(query.with_entities(Opportunity.opp_id))).scalar() or 0
    
    # Execute query
    opps = query.order_by(desc(Opportunity.crm_last_updated_at)).offset(skip).limit(limit).all()
    results = []
    for o in opps:
        practice_name = "General"
        if o.primary_practice_id:
            practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
            if practice: practice_name = practice.practice_name
        
        latest_score = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == o.opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        status = o.workflow_status
        if not status or status == 'OPEN':
            if latest_score:
                if latest_score.status == 'SUBMITTED': status = "SUBMITTED_FOR_REVIEW"
                elif latest_score.status == 'DRAFT': status = "UNDER_ASSESSMENT"
                else: status = latest_score.status
            else: status = "NEW"
        
        results.append({
            "id": o.opp_id,
            "row_id": o.opp_id,
            "remote_id": o.opp_number or "N/A",
            "name": o.opp_name,
            "customer": o.customer_name,
            "customer_name": o.customer_name,
            "practice": practice_name,
            "deal_value": o.deal_value or 0.0,
            "margin_percentage": o.margin_percentage or 0.0,
            "pat_margin": o.pat_margin or 0.0,
            "currency": o.currency or "USD",
            "workflow_status": status,
            "sales_stage": o.stage or "Qualifying",
            "bid_manager_user_id": o.bid_manager_user_id,
            "bid_manager": gname(db, o.bid_manager_user_id),
            "geo": o.geo or "Global",
            "close_date": o.close_date.strftime("%Y-%m-%d") if o.close_date else None,
            "sales_owner": gname(db, o.sales_owner_user_id) or "N/A",
            "assigned_practice_head": gname(db, o.assigned_practice_head_ids),
            "assigned_sales_head": gname(db, o.assigned_sales_head_id),
            "assigned_sa": gname(db, o.assigned_sa_ids),
            "assigned_sp": gname(db, o.assigned_sp_id),
            "assigned_finance": gname(db, o.assigned_finance_id),
            "assigned_legal": gname(db, o.assigned_legal_id),
            "win_probability": latest_score.overall_score if latest_score else 0,
            "overall_score": latest_score.overall_score if latest_score else 0,
            "version_no": latest_score.version_no if latest_score else None,
            "gh_approval_status": o.gh_approval_status or 'PENDING',
            "ph_approval_status": o.ph_approval_status or 'PENDING',
            "sh_approval_status": o.sh_approval_status or 'PENDING',
            "legal_approval_status": o.legal_approval_status or 'PENDING',
            "finance_approval_status": o.finance_approval_status or 'PENDING',
            "assigned_practice_head_ids": o.assigned_practice_head_ids or [],
            "assigned_sales_head_id": o.assigned_sales_head_id,
            "assigned_sa_ids": o.assigned_sa_ids or [],
            "assigned_sp_id": o.assigned_sp_id,
            "assigned_finance_id": o.assigned_finance_id,
            "assigned_legal_id": o.assigned_legal_id,
            "combined_submission_ready": o.combined_submission_ready or False,
            "recommendation": latest_score.recommendation if latest_score else None,
            "confidence_level": latest_score.confidence_level if latest_score else None
        })
    
    # Tab Counts (simplified for service)
    counts = {} # Router will probably still calculate these or we can move them here later if needed
    last_sync = db.query(func.max(Opportunity.local_last_synced_at)).scalar()

    return {
        "items": results,
        "total_count": total_count,
        "total_value": pipeline_value,
        "last_synced_at": last_sync
    }

def get_opportunity_counts_logic(
    db: Session,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    current_user_email: Optional[str] = None
):
    rev_stats = ['READY_FOR_REVIEW', 'UNDER_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'PENDING_GH_APPROVAL', 'PENDING_FINAL_APPROVAL', 'SUBMITTED', 'SUBMITTED_FOR_REVIEW']
    comp_stats = ['APPROVED', 'REJECTED', 'ACCEPTED', 'COMPLETED', 'WON', 'LOST']

    base_role = db.query(Opportunity).filter(Opportunity.is_active == True)
    base_role = base_role.outerjoin(AppUser, Opportunity.sales_owner_user_id == AppUser.user_id)
    
    hierarchy_filter = (AppUser.manager_email == current_user_email) if current_user_email else False

    if role in ('GH', 'ADMIN'):
        pass  # Full visibility
    elif role == 'BM':
        base_role = base_role.filter(
            Opportunity.bid_manager_user_id == user_id
        ) if user_id else base_role.filter(False)
    elif role == 'PH':
        base_role = base_role.filter(or_(
            cast(Opportunity.assigned_practice_head_ids, String).like(f'%"{user_id}"%'),
            hierarchy_filter
        )) if user_id else base_role.filter(False)
    elif role == 'SH':
        base_role = base_role.filter(or_(
            Opportunity.assigned_sales_head_id == user_id,
            hierarchy_filter
        )) if user_id else base_role.filter(False)
    elif role == 'SA':
        base_role = base_role.filter(or_(
            cast(Opportunity.assigned_sa_ids, String).like(f'%"{user_id}"%'),
            hierarchy_filter
        )) if user_id else base_role.filter(False)
    elif role == 'SP':
        base_role = base_role.filter(or_(
            Opportunity.assigned_sp_id == user_id,
            hierarchy_filter
        )) if user_id else base_role.filter(False)
    elif role in ('LEGAL', 'LL'):
        base_role = base_role.filter(or_(
            Opportunity.assigned_legal_id == user_id,
            hierarchy_filter
        )) if user_id else base_role.filter(False)
    elif role == 'FINANCE':
        base_role = base_role.filter(or_(
            Opportunity.assigned_finance_id == user_id,
            hierarchy_filter
        )) if user_id else base_role.filter(False)

    counts = {}
    if role == 'BM':
        current = base_role.filter(Opportunity.workflow_status != 'CLOSED').count()
        closed = base_role.filter(Opportunity.workflow_status == 'CLOSED').count()
        counts = {
            "all": base_role.count(),
            "current-assignments": current,
            "closed": closed,
        }
    elif role == 'PH':
        f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.ph_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED']))).count()
        f_rev = base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count()
        f_act_assign = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sa_id.is_(None))).count()
        f_act_approve = base_role.filter(and_(Opportunity.workflow_status.in_(rev_stats), Opportunity.ph_approval_status == 'PENDING')).count()
        counts = {"all": base_role.count(), "action-required": f_act_assign + f_act_approve, "in-progress": base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sa_id.isnot(None))).count(), "review": f_rev, "completed": f_comp}
    elif role == 'SH':
        f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.sh_approval_status.in_(['APPROVED', 'REJECTED', 'NOTIFIED']))).count()
        f_rev = base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count()
        f_act_assign = base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sp_id.is_(None))).count()
        f_act_approve = base_role.filter(and_(Opportunity.workflow_status.in_(rev_stats), Opportunity.sh_approval_status == 'PENDING')).count()
        counts = {"all": base_role.count(), "action-required": f_act_assign + f_act_approve, "in-progress": base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.assigned_sp_id.isnot(None))).count(), "review": f_rev, "completed": f_comp}
    elif role in ['SA', 'SP', 'LEGAL', 'FINANCE', 'LL']:
        f_comp = base_role.filter(or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.workflow_status.in_([f"{role}_SUBMITTED", 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'PENDING_GH_APPROVAL', 'SUBMITTED']))).count()
        counts = {"all": base_role.count(), "action-required": base_role.filter(and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats + ['UNDER_ASSESSMENT', 'IN_ASSESSMENT']), Opportunity.workflow_status.isnot(None))).count(), "in-progress": base_role.filter(Opportunity.workflow_status.in_(['UNDER_ASSESSMENT', 'IN_ASSESSMENT'])).count(), "submitted": base_role.filter(Opportunity.workflow_status.in_(rev_stats)).count(), "completed": f_comp}
    else:
        f_rev = Opportunity.workflow_status.in_(rev_stats)
        f_comp = or_(Opportunity.workflow_status.in_(comp_stats), Opportunity.gh_approval_status.in_(['APPROVED', 'REJECTED']))
        f_open = and_(Opportunity.workflow_status.notin_(comp_stats + rev_stats), Opportunity.workflow_status.isnot(None))
        counts = {"all": base_role.count(), "unassigned": base_role.filter(and_(f_open, or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.is_(None))).count(), "review": base_role.filter(f_rev).count(), "completed": base_role.filter(f_comp).count()}
        counts['in-progress'] = base_role.filter(and_(f_open, or_(and_(Opportunity.assigned_practice_head_ids != None, cast(Opportunity.assigned_practice_head_ids, String) != '[]'), Opportunity.assigned_sales_head_id.isnot(None)))).count()
        counts['action-required'] = base_role.filter(and_(f_open, or_(or_(Opportunity.assigned_practice_head_ids == None, cast(Opportunity.assigned_practice_head_ids, String) == '[]'), Opportunity.assigned_sales_head_id.is_(None)))).count()
    return counts

def get_opportunity_by_id_logic(db: Session, opp_id: str):
    o = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not o: return None
    
    practice_name = "General"
    if o.primary_practice_id:
        practice = db.query(Practice).filter(Practice.practice_id == o.primary_practice_id).first()
        if practice: practice_name = practice.practice_name
    
    latest_score = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == o.opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    has_ratings = False
    if latest_score:
        has_ratings = db.query(OppScoreSectionValue).filter(
            OppScoreSectionValue.score_version_id == latest_score.score_version_id,
            OppScoreSectionValue.score > 0
        ).first() is not None

    status = o.workflow_status
    spec_states = {'OPEN', 'ACTIVE', 'CLOSED', 'REOPENED'}
    if not status or (status not in spec_states and status in ['ASSIGNED_TO_SA', 'ASSIGNED_TO_SP']):
        if latest_score:
            if latest_score.status == 'SUBMITTED': status = "SUBMITTED"
            elif latest_score.status in ['APPROVED', 'REJECTED']: status = latest_score.status
            elif has_ratings: status = "UNDER_ASSESSMENT"
            elif (o.assigned_sa_ids and len(o.assigned_sa_ids) > 0) or o.assigned_sp_id: status = "ASSIGNED"
            else: status = "NEW"
        elif (o.assigned_sa_ids and len(o.assigned_sa_ids) > 0) or o.assigned_sp_id: status = "ASSIGNED"
        else: status = "NEW"

    if status not in spec_states and o.workflow_status == "UNDER_ASSESSMENT" and status in ["NEW", "ASSIGNED"]:
        status = "UNDER_ASSESSMENT"

    return {
        "id": o.opp_id,
        "row_id": o.opp_id,
        "remote_id": o.opp_number or "N/A",
        "name": o.opp_name,
        "customer": o.customer_name,
        "customer_name": o.customer_name,
        "practice": practice_name,
        "deal_value": o.deal_value or 0.0,
        "margin_percentage": o.margin_percentage or 0.0,
        "pat_margin": o.pat_margin or 0.0,
        "currency": o.currency or "USD",
        "workflow_status": status,
        "sales_stage": o.stage or "Qualifying",
        "geo": o.geo or "Global",
        "close_date": o.close_date.strftime("%Y-%m-%d") if o.close_date else None,
        "sales_owner": gname(db, o.sales_owner_user_id) or "N/A",
        "assigned_practice_head": gname(db, o.assigned_practice_head_ids),
        "assigned_sales_head": gname(db, o.assigned_sales_head_id),
        "assigned_sa": gname(db, o.assigned_sa_ids),
        "assigned_sp": gname(db, o.assigned_sp_id),
        "assigned_finance": gname(db, o.assigned_finance_id),
        "assigned_legal": gname(db, o.assigned_legal_id),
        "win_probability": latest_score.overall_score if latest_score else 0,
        "overall_score": latest_score.overall_score if latest_score else 0,
        "version_no": latest_score.version_no if latest_score else None,
        "gh_approval_status": o.gh_approval_status or 'PENDING',
        "ph_approval_status": o.ph_approval_status or 'PENDING',
        "sh_approval_status": o.sh_approval_status or 'PENDING',
        "legal_approval_status": o.legal_approval_status or 'PENDING',
        "finance_approval_status": o.finance_approval_status or 'PENDING',
        "assigned_practice_head_ids": o.assigned_practice_head_ids or [],
        "assigned_sales_head_id": o.assigned_sales_head_id,
        "assigned_sa_ids": o.assigned_sa_ids or [],
        "assigned_sp_id": o.assigned_sp_id,
        "assigned_finance_id": o.assigned_finance_id,
        "assigned_legal_id": o.assigned_legal_id,
        "combined_submission_ready": o.combined_submission_ready or False,
        "recommendation": latest_score.recommendation if latest_score else None,
        "confidence_level": latest_score.confidence_level if latest_score else None
    }

def assign_role_logic(db: Session, opp_id: str, role: str, target_user_id: str):
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp: return None
    
    if role == 'PH': opp.assigned_practice_head_id = target_user_id
    elif role == 'SH': opp.assigned_sales_head_id = target_user_id
    elif role == 'SA': opp.assigned_sa_id = target_user_id
    elif role == 'SP': opp.assigned_sp_id = target_user_id

    if role in ['SA', 'SP']:
        latest = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
        if latest:
            if role == 'SA': latest.sa_submitted = False
            if role == 'SP': latest.sp_submitted = False
            if latest.status == 'SUBMITTED': latest.status = 'UNDER_ASSESSMENT'
        
        if not opp.workflow_status or opp.workflow_status in ['READY_FOR_REVIEW', 'SA_SUBMITTED', 'SP_SUBMITTED', 'UNDER_REVIEW', 'SUBMITTED']:
            opp.workflow_status = "UNDER_ASSESSMENT"

    db.commit()
    return {"status": "success"}

from sqlalchemy.orm import joinedload

class OpportunityService:
    @staticmethod
    def calculate_overall_score(db: Session, score_version_id: str) -> int:
        """
        Calculates the weighted overall score for a specific assessment version.
        Formula: (sum(score * weight) / (sum(weight) * 5)) * 100
        Returns an integer percentage (0-100).
        """
        total_w, weighted_s = 0, 0
        vals = db.query(OppScoreSectionValue).options(joinedload(OppScoreSectionValue.section)).filter(
            OppScoreSectionValue.score_version_id == score_version_id
        ).all()
        
        for v in vals:
            if v.section:
                weighted_s += (v.score * v.section.weight)
                total_w += v.section.weight
        
        max_s = total_w * 5
        return int((weighted_s / max_s) * 100) if max_s > 0 else 0

    @staticmethod
    def evaluate_compliance_routing(opp_id: str, db: Session):
        """
        Enforce MVP business rules.
        If deal_value > 5 Crores (50,000,000) AND margin_percentage < 5.0,
        set finance_approval_status and legal_approval_status to 'PENDING_MANDATORY'.
        """
        opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
        if not opp:
            return

        if opp.deal_value and opp.deal_value > 50000000.0:
            if opp.margin_percentage is not None and opp.margin_percentage < 5.0:
                opp.finance_approval_status = 'PENDING_MANDATORY'
                opp.legal_approval_status = 'PENDING_MANDATORY'
                db.flush()

    @staticmethod
    def evaluate_go_no_go(db: Session, overall_score: int) -> str:
        """
        Determines GO or NO_GO recommendation based on the configurable threshold
        stored in system_config. Defaults to 80% if config is missing.
        Returns 'GO' or 'NO_GO'.
        """
        from backend.app.models import SystemConfig as _SystemConfig
        cfg = db.query(_SystemConfig).filter(
            _SystemConfig.config_key == 'go_no_go_threshold_percent'
        ).first()

        threshold = 80  # safe default
        if cfg and isinstance(cfg.config_value, dict):
            threshold = cfg.config_value.get('threshold', 80)

        return 'GO' if overall_score > threshold else 'NO_GO'

