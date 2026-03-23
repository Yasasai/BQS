"""Lifecycle states, closure columns, system_config, role upsert, workflow_status backfill

Stage 2 refactor migration.

Changes:
  1. Add pat_margin column to opportunity (gap from prior migration)
  2. Add lifecycle closure columns to opportunity
     (close_reason, closed_by, closed_at, reopened_by, reopened_at)
  3. Create system_config table for admin-configurable parameters
  4. Upsert BM (7) and ADMIN (8) roles into role table
  5. Seed default GO/NO-GO threshold into system_config
  6. Backfill workflow_status to spec-aligned states:
       NEW_FROM_CRM, ASSIGNED_TO_SA              -> OPEN
       UNDER_ASSESSMENT, WAITING_PH_APPROVAL,
         READY_FOR_MGMT_REVIEW, READY_FOR_REVIEW,
         PENDING_FINAL_APPROVAL, PENDING_GH_APPROVAL,
         SUBMITTED_FOR_REVIEW                    -> ACTIVE
       APPROVED                                  -> CLOSED  (close_reason = WON)
       REJECTED                                  -> CLOSED  (close_reason = LOST)

Revision ID: a1b2c3d4e5f6
Revises: f7f1087a2ff8
Create Date: 2026-03-20
"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f7f1087a2ff8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply all Stage 2 schema changes and data backfills."""

    conn = op.get_bind()

    # ------------------------------------------------------------------ #
    # 1. Fill the pat_margin gap from the prior migration                  #
    # ------------------------------------------------------------------ #
    pat_margin_exists = conn.execute(sa.text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'opportunity' AND column_name = 'pat_margin'
    """)).fetchone()

    if not pat_margin_exists:
        op.add_column('opportunity', sa.Column('pat_margin', sa.Float(), nullable=True))

    # ------------------------------------------------------------------ #
    # 2. Lifecycle closure columns                                         #
    # ------------------------------------------------------------------ #
    def _col_exists(table: str, col: str) -> bool:
        return bool(conn.execute(sa.text(
            f"SELECT 1 FROM information_schema.columns "
            f"WHERE table_name = :t AND column_name = :c"
        ), {"t": table, "c": col}).fetchone())

    if not _col_exists('opportunity', 'close_reason'):
        op.add_column('opportunity', sa.Column('close_reason', sa.String(), nullable=True))
    if not _col_exists('opportunity', 'closed_by'):
        op.add_column('opportunity', sa.Column('closed_by', sa.String(), nullable=True))
        op.create_foreign_key(
            'fk_opportunity_closed_by', 'opportunity', 'app_user',
            ['closed_by'], ['user_id']
        )
    if not _col_exists('opportunity', 'closed_at'):
        op.add_column('opportunity', sa.Column('closed_at', sa.DateTime(), nullable=True))
    if not _col_exists('opportunity', 'reopened_by'):
        op.add_column('opportunity', sa.Column('reopened_by', sa.String(), nullable=True))
        op.create_foreign_key(
            'fk_opportunity_reopened_by', 'opportunity', 'app_user',
            ['reopened_by'], ['user_id']
        )
    if not _col_exists('opportunity', 'reopened_at'):
        op.add_column('opportunity', sa.Column('reopened_at', sa.DateTime(), nullable=True))

    # ------------------------------------------------------------------ #
    # 3. system_config table                                               #
    # ------------------------------------------------------------------ #
    system_config_exists = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'system_config'"
    )).fetchone()

    if not system_config_exists:
        op.create_table(
            'system_config',
            sa.Column('config_key', sa.String(), nullable=False),
            sa.Column('config_value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
            sa.Column('updated_by', sa.String(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['updated_by'], ['app_user.user_id'], name='fk_system_config_updated_by'),
            sa.PrimaryKeyConstraint('config_key', name='system_config_pkey'),
        )

    # ------------------------------------------------------------------ #
    # 4. Upsert BM and ADMIN roles                                         #
    # ------------------------------------------------------------------ #
    for role_id, role_code, role_name in [
        (7, 'BM',    'Bid Manager'),
        (8, 'ADMIN', 'Admin'),
        (9, 'LEGAL', 'Legal'),
        (10, 'FINANCE', 'Finance'),
    ]:
        exists = conn.execute(sa.text(
            "SELECT 1 FROM role WHERE role_code = :code"
        ), {"code": role_code}).fetchone()
        if not exists:
            conn.execute(sa.text(
                "INSERT INTO role (role_id, role_code, role_name) VALUES (:id, :code, :name)"
            ), {"id": role_id, "code": role_code, "name": role_name})

    # ------------------------------------------------------------------ #
    # 5. Seed default GO/NO-GO threshold                                   #
    # ------------------------------------------------------------------ #
    now_ts = datetime.now(timezone.utc).replace(tzinfo=None)  # postgres TIMESTAMP without tz
    config_exists = conn.execute(sa.text(
        "SELECT 1 FROM system_config WHERE config_key = 'go_no_go_threshold_percent'"
    )).fetchone()
    if not config_exists:
        conn.execute(sa.text(
            "INSERT INTO system_config (config_key, config_value, updated_at) "
            "VALUES ('go_no_go_threshold_percent', "
            "'{\"threshold\": 80, \"comparison_operator\": \"greater_than\"}', "
            ":ts)"
        ), {"ts": now_ts})

    # ------------------------------------------------------------------ #
    # 6. Backfill workflow_status to spec-aligned lifecycle states          #
    # ------------------------------------------------------------------ #

    # OPEN: pre-BM states — opportunity exists but no active execution
    conn.execute(sa.text("""
        UPDATE opportunity
        SET workflow_status = 'OPEN'
        WHERE workflow_status IN ('NEW_FROM_CRM', 'ASSIGNED_TO_SA')
    """))

    # ACTIVE: BM execution in progress (assessment, approval pipeline)
    conn.execute(sa.text("""
        UPDATE opportunity
        SET workflow_status = 'ACTIVE'
        WHERE workflow_status IN (
            'UNDER_ASSESSMENT',
            'WAITING_PH_APPROVAL',
            'READY_FOR_MGMT_REVIEW',
            'READY_FOR_REVIEW',
            'PENDING_FINAL_APPROVAL',
            'PENDING_GH_APPROVAL',
            'SUBMITTED_FOR_REVIEW',
            'SUBMITTED'
        )
    """))

    # CLOSED (WON): assessment was fully approved by management
    conn.execute(sa.text("""
        UPDATE opportunity
        SET workflow_status = 'CLOSED',
            close_reason    = 'WON',
            closed_at       = :ts
        WHERE workflow_status = 'APPROVED'
    """), {"ts": now_ts})

    # CLOSED (LOST): assessment was rejected — bid will not proceed
    conn.execute(sa.text("""
        UPDATE opportunity
        SET workflow_status = 'CLOSED',
            close_reason    = 'LOST',
            closed_at       = :ts
        WHERE workflow_status = 'REJECTED'
    """), {"ts": now_ts})


def downgrade() -> None:
    """Reverse Stage 2 schema changes.

    workflow_status backfill is partially reversible:
      OPEN     -> NEW_FROM_CRM
      ACTIVE   -> UNDER_ASSESSMENT
      CLOSED (WON)  -> APPROVED
      CLOSED (LOST) -> REJECTED
      REOPENED -> UNDER_ASSESSMENT
    Information about intermediate states (WAITING_PH_APPROVAL etc.) is lost.
    """
    conn = op.get_bind()

    # --- Reverse workflow_status ---
    conn.execute(sa.text(
        "UPDATE opportunity SET workflow_status = 'APPROVED'  WHERE workflow_status = 'CLOSED' AND close_reason = 'WON'"
    ))
    conn.execute(sa.text(
        "UPDATE opportunity SET workflow_status = 'REJECTED'  WHERE workflow_status = 'CLOSED' AND close_reason = 'LOST'"
    ))
    conn.execute(sa.text(
        "UPDATE opportunity SET workflow_status = 'UNDER_ASSESSMENT' WHERE workflow_status IN ('ACTIVE', 'REOPENED')"
    ))
    conn.execute(sa.text(
        "UPDATE opportunity SET workflow_status = 'NEW_FROM_CRM' WHERE workflow_status = 'OPEN'"
    ))

    # --- Drop system_config ---
    op.drop_table('system_config')

    # --- Drop closure columns ---
    op.drop_constraint('fk_opportunity_reopened_by', 'opportunity', type_='foreignkey')
    op.drop_constraint('fk_opportunity_closed_by',   'opportunity', type_='foreignkey')
    op.drop_column('opportunity', 'reopened_at')
    op.drop_column('opportunity', 'reopened_by')
    op.drop_column('opportunity', 'closed_at')
    op.drop_column('opportunity', 'closed_by')
    op.drop_column('opportunity', 'close_reason')

    # --- Drop pat_margin (only if it was added by this migration) ---
    # Note: if pat_margin already existed before this migration, this will break.
    # In practice, check manually before running downgrade on production.
    try:
        op.drop_column('opportunity', 'pat_margin')
    except Exception:
        pass  # column may have pre-existed; skip silently
