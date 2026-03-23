# 16_bid_management_rbac_workflow_refactor.md
 
## 1. Purpose
 
This specification defines the refactor requirements for the Bid Management module to address:

- role-based access and visibility defects

- missing workflow controls

- assignment reflection issues

- admin governance gaps

- missing Bid Manager execution features

- lifecycle and closure inconsistencies
 
This document is the target-state contract for the module refactor.
 
---
 
## 2. Objectives
 
The refactor must achieve the following outcomes:
 
1. Enforce clear RBAC across all relevant roles

2. Fix opportunity, assessment, and document visibility logic

3. Ensure assignments reflect correctly under user worklists

4. Establish a controlled opportunity lifecycle

5. Complete the Bid Manager execution workflow

6. Introduce Admin-only governance controls

7. Prevent privilege leakage across roles

8. Add auditability for sensitive admin actions

9. Enforce key validation rules at API and persistence layers

10. Cleanly separate current work from closed work
 
---
 
## 3. Scope
 
This refactor applies to:
 
- opportunity visibility

- opportunity assignment

- assessment access and scoring

- document access

- Bid Manager workflow

- pursuit team creation

- legal team assignment

- current assignments view

- closed opportunities view

- close and reopen logic

- admin role capabilities

- audit trail logging

- RBAC enforcement at UI and API levels
 
Out of scope unless explicitly wired later:

- advanced analytics

- control-plane signals

- notifications

- external workflow orchestration

- approval workflow beyond roles defined here
 
---
 
## 4. Business Context
 
The Bid Management module is used to manage bid evaluation and execution for opportunities.
 
The current implementation has the following issues:

- some assigned users cannot see the opportunity or assessment they are expected to work on

- visibility rules are inconsistent across pursuit, sales, and practice roles

- admin and global-head powers are not clearly separated

- assignment changes are not always reflected in user worklists

- closed-state behavior is not fully enforced

- Bid Manager flow is incomplete
 
This refactor standardizes the operating model.
 
---
 
## 5. Role Model
 
### 5.1 Supported Roles
 
The system must support the following roles:
 
- `ADMIN`

- `GLOBAL_HEAD`

- `PRACTICE_HEAD`

- `SALES_HEAD`

- `SALES_PERSON`

- `BID_MANAGER`

- `PURSUIT_TEAM`

- `FINANCE`

- `LEGAL`
 
### 5.2 Role Intent
 
#### ADMIN

System-wide governance role with authority over assignments, user-level overrides, and reopen actions.
 
#### GLOBAL_HEAD

Enterprise leadership role with broad visibility across opportunities but without admin functions.
 
#### PRACTICE_HEAD

Practice-level leader who must see opportunities and assessments relevant to the practice or where explicitly assigned.
 
#### SALES_HEAD

Sales hierarchy role with visibility aligned to the opportunity ownership hierarchy and explicit assignments.
 
#### SALES_PERSON

Direct sales owner or sales-linked user for the opportunity.
 
#### BID_MANAGER

Primary execution owner for bid scoring, team setup, financial input coordination, and document handling.
 
#### PURSUIT_TEAM

Supporting contributors who should see the opportunity, assessment, and documents for opportunities where they are part of the pursuit team.
 
#### FINANCE

Support role for PAT and margin-related input.
 
#### LEGAL

Support role for legal review participation.
 
---
 
## 6. Core Access Principles
 
### 6.1 General Principles
 
1. Visibility must be granted by role, explicit assignment, or hierarchy mapping

2. Action permission must be distinct from read visibility

3. Broad visibility does not imply admin control

4. UI hiding is not sufficient; API authorization is mandatory

5. Closed opportunities must be read-only except for explicit Admin reopen

6. Any user assigned to a work item must see it in their worklist

7. Pursuit team members must see both assessment and documents for their assigned opportunities
 
### 6.2 No Privilege Leakage
 
The following are explicitly prohibited:

- Global Head inheriting Admin controls

- hidden UI actions remaining callable through API

- non-admin reopening closed opportunities

- closed opportunities being editable after closure

- unassigned users seeing restricted opportunity data without role basis
 
---
 
## 7. RBAC Specification
 
## 7.1 Visibility Matrix
 
| Capability / Entity | ADMIN | GLOBAL_HEAD | PRACTICE_HEAD | SALES_HEAD / SALES_PERSON | BID_MANAGER | PURSUIT_TEAM | FINANCE | LEGAL |

|---|---|---|---|---|---|---|---|---|

| View all opportunities | Yes | Yes | No | No | No | No | No | No |

| View practice opportunities | Yes | Yes | Yes | As mapped | No | No | No | No |

| View assigned opportunities | Yes | Yes | Yes | Yes | Yes | Yes | Yes if assigned | Yes if assigned |

| View assessments for visible opportunities | Yes | Yes | Yes | Yes | Yes | Yes | As needed | As needed |

| View documents for visible opportunities | Yes | Yes | Yes | Yes | Yes | Yes | As needed | As needed |
 
### 7.2 Notes
 
- Practice Head must be able to see the assessment she has been assigned in the pursuit team context

- Sales hierarchy must be able to see the opportunity similarly to pursuit-team access where relevant

- Pursuit team must see both assessments and documents

- Global Head must be visible across all opportunities

- Global Head assignment must be controlled by Admin

- Global Head must not receive Admin features
 
---
 
## 8. Action Permission Matrix
 
| Action | ADMIN | GLOBAL_HEAD | PRACTICE_HEAD | SALES | BID_MANAGER | PURSUIT_TEAM | FINANCE | LEGAL |

|---|---|---|---|---|---|---|---|---|

| Assign Bid Manager | Yes | Yes | No | No | No | No | No | No |

| Reassign Bid Manager | Yes | Yes | No | No | No | No | No | No |

| View assessment | Yes | Yes | Yes | Yes | Yes | Yes | As assigned | As assigned |

| Edit assessment score | Yes | No | No | No | Yes | No | No | No |

| Submit assessment | Yes | No | No | No | Yes | No | No | No |

| Enter PAT | Yes | No | No | No | Yes | No | Support | No |

| Enter Margin | Yes | No | No | No | Yes | No | Support | No |

| Upload documents | Yes | No | No | No | Yes | No | No | No |

| Create pursuit team | Yes | No | No | No | Yes | No | No | No |

| Select legal team | Yes | No | No | No | Yes | No | No | No |

| Close opportunity | No | No | No | No | Yes | No | No | No |

| Reopen closed opportunity | Yes | No | No | No | No | No | No | No |

| Edit user values | Yes | No | No | No | No | No | No | No |

| Assign Global Head | Yes | No | No | No | No | No | No | No |
 
### 8.1 Clarifications
 
- Global Head can change Bid Manager assignment but must not get Admin control functions

- Admin is the only role allowed to reopen closed opportunities

- Admin is the only role allowed to edit protected user-level administrative values

- Bid Manager owns operational execution but not system governance
 
---
 
## 9. Opportunity Lifecycle
 
### 9.1 States
 
The opportunity lifecycle must support the following states:
 
- `OPEN`

- `ACTIVE`

- `CLOSED`

- `REOPENED`
 
### 9.2 State Definitions
 
#### OPEN

Opportunity exists and is available for assignment.

No Bid Manager execution has been completed yet.
 
#### ACTIVE

Opportunity is in progress.

Bid workflow is underway.
 
#### CLOSED

Opportunity is finalized.

Closure is allowed only when rules are satisfied.

No further edits are permitted.
 
#### REOPENED

Opportunity was previously closed and has been reopened by Admin.

It returns to active working state under controlled conditions.
 
### 9.3 State Transition Rules
 
| From | To | Allowed By | Conditions |

|---|---|---|---|

| OPEN | ACTIVE | Admin / Global Head / system logic | Bid Manager assigned or work started |

| ACTIVE | CLOSED | Bid Manager | Status is WON or LOST and final document uploaded |

| CLOSED | REOPENED | Admin | Explicit reopen action |

| REOPENED | CLOSED | Bid Manager | Same closure rules as ACTIVE |
 
### 9.4 Closed-State Restrictions
 
When an opportunity is `CLOSED`:

- assessment edits must be blocked

- PAT and margin edits must be blocked

- document modifications must be blocked unless reopen occurs

- pursuit team edits must be blocked

- opportunity must appear under Closed Opportunities

- opportunity must not appear as editable under Current Assignments
 
---
 
## 10. Assignment Logic
 
### 10.1 Open Opportunity Assignment
 
Open opportunities should be assigned to Bid Managers through defined business logic or manual override.
 
Assignment may be changed by:

- Admin

- Global Head
 
### 10.2 Worklist Reflection Rule
 
Any opportunity or work item assigned to a user must appear under that user’s `Current Assignments`.
 
This applies to:

- Bid Manager

- Pursuit Team

- Practice Head where assignment exists

- Sales-linked users where assignment or hierarchy logic applies
 
### 10.3 Assignment Consistency Rules
 
- assignment changes must reflect in UI and API

- stale assignment display is not acceptable

- inactive assignments must not appear as active work items

- assignment must be backed by persistent record, not UI-only state
 
---
 
## 11. Bid Manager Workflow
 
### 11.1 Functional Responsibilities
 
Bid Manager is responsible for:

- performing and submitting assessment

- entering score

- triggering GO / NO-GO logic

- entering PAT

- entering Margin

- uploading documents

- creating pursuit team

- selecting legal team

- driving close action when conditions are met
 
### 11.2 Scoring Logic
 
The Bid Manager must be able to:

- edit assessment score

- submit assessment
 
### 11.3 GO / NO-GO Rule
 
A configurable threshold must determine GO vs NO-GO.
 
Default rule:

- if score is greater than 80%, flag as `GO`

- otherwise flag as `NO_GO`
 
This threshold must be configurable through JSON-based configuration and must not be hardcoded in business logic.
 
### 11.4 Configuration Example
 
```json

{

  "go_no_go_threshold_percent": 80,

  "comparison_operator": "greater_than"

}
 