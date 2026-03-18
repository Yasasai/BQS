from sqlalchemy.orm import Session
from backend.app.models import Opportunity, AppUser, OppScoreVersion
from fastapi import HTTPException
from sqlalchemy import desc
from datetime import datetime, timezone

def handle_approval_action(db: Session, opp_id: str, role: str, decision: str, comment: str = None, user_id: str = None):
    """
    Core workflow logic for processing stakeholder approvals and status transitions.
    (Task 4: Reduce Fat Router logic)
    """
    opp = db.query(Opportunity).filter(Opportunity.opp_id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    decision = decision.upper()
    if 'APPROVE' in decision: decision = 'APPROVED'
    if 'REJECT' in decision: decision = 'REJECTED'

    if role == 'GH':
        opp.gh_approval_status = decision
        # Special Rule: Fast Track (3.5 to 4.0)
        if opp.workflow_status == 'PENDING_GH_APPROVAL' and decision == 'APPROVED':
            opp.workflow_status = 'APPROVED'
            db.commit()
            return {"status": "success", "message": "Fast-track approval completed by GH"}
    elif role == 'PH':
        opp.ph_approval_status = decision
    elif role == 'SH':
        opp.sh_approval_status = decision
    elif role == 'LEGAL':
        opp.legal_approval_status = decision
    elif role == 'FINANCE':
        opp.finance_approval_status = decision
    elif role == 'LL':
        opp.legal_approval_status = decision

    # Persistent Audit Log: Update latest version with decision
    latest_ver = db.query(OppScoreVersion).filter(OppScoreVersion.opp_id == opp_id).order_by(desc(OppScoreVersion.version_no)).first()
    if latest_ver:
        decision_label = f"[{role} {decision}]"
        current_comment = latest_ver.summary_comment or ""
        comment_text = comment or "No comment provided."
        latest_ver.summary_comment = f"{decision_label}: {comment_text}\n---\n{current_comment}"
        
        # Final status updates for the version
        if decision == 'REJECTED':
            latest_ver.status = 'REJECTED'
        elif (opp.gh_approval_status == 'APPROVED' and 
              opp.ph_approval_status == 'APPROVED' and 
              opp.sh_approval_status == 'APPROVED' and
              (opp.legal_approval_status == 'APPROVED' or opp.legal_approval_status == 'PENDING') and
              (opp.finance_approval_status == 'APPROVED' or opp.finance_approval_status == 'PENDING')):
            latest_ver.status = 'APPROVED'

    # Update Opportunity workflow status
    if decision == 'REJECTED':
        opp.workflow_status = 'REJECTED'
    elif (opp.gh_approval_status == 'APPROVED' and 
          opp.ph_approval_status == 'APPROVED' and 
          opp.sh_approval_status == 'APPROVED' and
          (opp.legal_approval_status == 'APPROVED' or opp.legal_approval_status == 'PENDING') and
          (opp.finance_approval_status == 'APPROVED' or opp.finance_approval_status == 'PENDING')):
        opp.workflow_status = 'APPROVED'
    else:
        if opp.workflow_status != 'PENDING_GH_APPROVAL':
            opp.workflow_status = 'PENDING_FINAL_APPROVAL'

    db.commit()
    return {"status": "success", "workflow_status": opp.workflow_status}
