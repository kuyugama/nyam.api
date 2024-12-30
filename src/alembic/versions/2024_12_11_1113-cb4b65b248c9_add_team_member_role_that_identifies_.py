"""Add team_member_role that identifies whether role can be used for team member

Revision ID: cb4b65b248c9
Revises: 7ac1ccf53394
Create Date: 2024-12-11 11:13:01.304056

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cb4b65b248c9"
down_revision: Union[str, None] = "7ac1ccf53394"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_roles",
        sa.Column("team_member_role", sa.Boolean(), nullable=False, server_default="false"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service_roles", "team_member_role")
    # ### end Alembic commands ###
