"""Add verifier to teams

Revision ID: 730fea4159bd
Revises: 532b67ccf93c
Create Date: 2024-12-24 10:41:58.269117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '730fea4159bd'
down_revision: Union[str, None] = '532b67ccf93c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_teams', sa.Column('verifier_id', sa.BIGINT(), nullable=True))
    op.create_index(op.f('ix_service_teams_verifier_id'), 'service_teams', ['verifier_id'], unique=False)
    op.create_foreign_key(None, 'service_teams', 'service_users', ['verifier_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'service_teams', type_='foreignkey')
    op.drop_index(op.f('ix_service_teams_verifier_id'), table_name='service_teams')
    op.drop_column('service_teams', 'verifier_id')
    # ### end Alembic commands ###
