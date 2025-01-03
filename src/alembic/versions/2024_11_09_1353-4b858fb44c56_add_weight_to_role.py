"""Add weight to role

Revision ID: 4b858fb44c56
Revises: 00f20e72f05f
Create Date: 2024-11-09 13:53:52.244491

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b858fb44c56"
down_revision: Union[str, None] = "00f20e72f05f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service_roles", sa.Column("weight", sa.Integer(), server_default="0", nullable=False)
    )
    op.create_index(op.f("ix_service_roles_weight"), "service_roles", ["weight"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_service_roles_weight"), table_name="service_roles")
    op.drop_column("service_roles", "weight")
    # ### end Alembic commands ###
