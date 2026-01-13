"""
BQS Constants - Shared Enums and Status Definitions
====================================================

This file defines all status enums and constants used across
both Frontend and Backend to avoid "magic strings".

Usage (Backend):
    from constants import WorkflowStatus
    opp.workflow_status = WorkflowStatus.NEW_FROM_CRM

Usage (Frontend):
    import { WorkflowStatus } from '../constants';
    if (opp.workflow_status === WorkflowStatus.WAITING_PH_APPROVAL) { ... }
"""

class WorkflowStatus:
    """Workflow status enum - matches database column exactly"""
    
    # Initial States
    NEW_FROM_CRM = "NEW_FROM_CRM"
    ASSIGNED_TO_PRACTICE = "ASSIGNED_TO_PRACTICE"
    
    # SA States
    ASSIGNED_TO_SA = "ASSIGNED_TO_SA"
    UNDER_ASSESSMENT = "UNDER_ASSESSMENT"
    DRAFT_SCORE = "DRAFT_SCORE"
    
    # Practice Head States
    WAITING_PH_APPROVAL = "WAITING_PH_APPROVAL"
    REVIEW_PENDING = "REVIEW_PENDING"
    
    # Management States
    READY_FOR_MGMT_REVIEW = "READY_FOR_MGMT_REVIEW"
    PENDING_GOVERNANCE = "PENDING_GOVERNANCE"
    PENDING_FINAL_DECISION = "PENDING_FINAL_DECISION"
    
    # Final States
    COMPLETED_BID = "COMPLETED_BID"
    COMPLETED_NO_BID = "COMPLETED_NO_BID"
    
    @classmethod
    def all(cls):
        """Get all valid statuses"""
        return [
            cls.NEW_FROM_CRM,
            cls.ASSIGNED_TO_PRACTICE,
            cls.ASSIGNED_TO_SA,
            cls.UNDER_ASSESSMENT,
            cls.DRAFT_SCORE,
            cls.WAITING_PH_APPROVAL,
            cls.REVIEW_PENDING,
            cls.READY_FOR_MGMT_REVIEW,
            cls.PENDING_GOVERNANCE,
            cls.PENDING_FINAL_DECISION,
            cls.COMPLETED_BID,
            cls.COMPLETED_NO_BID
        ]
    
    @classmethod
    def is_valid(cls, status):
        """Check if status is valid"""
        return status in cls.all()

class PracticeHeadDecision:
    """Practice Head decision enum"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"

class ManagementDecision:
    """Management final decision enum"""
    GO = "GO"
    NO_GO = "NO_GO"
    PENDING = "PENDING"

class UserRole:
    """User role enum"""
    MANAGEMENT = "Management"
    PRACTICE_HEAD = "Practice Head"
    SOLUTION_ARCHITECT = "Solution Architect"
    SALES = "Sales"

class Currency:
    """Currency codes"""
    USD = "USD"
    SAR = "SAR"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    PHP = "PHP"

class SalesStage:
    """Oracle CRM sales stages"""
    QUALIFY = "1. Qualify"
    DEVELOP = "2. Develop"
    PROPOSE = "3. Propose"
    COMMIT = "4. Commit"
    CLOSE = "5. Close"

# Database Table Names
class Tables:
    OPPORTUNITIES = "opportunities"
    ASSESSMENTS = "assessments"
    USERS = "users"

# API Endpoints
class Endpoints:
    OPPORTUNITIES = "/api/opportunities"
    ORACLE_SYNC = "/api/sync-database"
    ASSIGN_PRACTICE = "/api/opportunities/{id}/assign-practice"
    ASSIGN_SA = "/api/opportunities/{id}/assign-sa"
    SEND_TO_PH = "/api/opportunities/{id}/send-to-practice-head"
    ACCEPT_SCORE = "/api/opportunities/{id}/accept-score"
    REJECT_SCORE = "/api/opportunities/{id}/reject-score"
    FINAL_DECISION = "/api/opportunities/{id}/final-decision"

# Export for easy imports
__all__ = [
    'WorkflowStatus',
    'PracticeHeadDecision',
    'ManagementDecision',
    'UserRole',
    'Currency',
    'SalesStage',
    'Tables',
    'Endpoints'
]
