"""add_locking_columns_to_opportunity

Revision ID: f5e1a2b3c4d5
Revises: b2ae11e9d9c6
Create Date: 2026-03-04 16:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f5e1a2b3c4d5'
down_revision: Union[str, Sequence[str], None] = 'b2ae11e9d9c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('opportunity', sa.Column('locked_by', sa.String(), nullable=True))
    op.add_column('opportunity', sa.Column('locked_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_opportunity_locked_by', 'opportunity', 'app_user', ['locked_by'], ['user_id'])

def downgrade() -> None:
    op.drop_constraint('fk_opportunity_locked_by', 'opportunity', type_='foreignkey')
    op.drop_column('opportunity', 'locked_at')
    op.drop_column('opportunity', 'locked_by')
