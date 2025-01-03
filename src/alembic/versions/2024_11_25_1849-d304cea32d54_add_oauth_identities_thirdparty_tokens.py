"""add oauth identities, thirdparty tokens

Revision ID: d304cea32d54
Revises: 6d3c32b28511
Create Date: 2024-11-25 18:49:35.731986

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d304cea32d54"
down_revision: Union[str, None] = "6d3c32b28511"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "service_oauth_identities",
        sa.Column("user_id", sa.BIGINT(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_user", sa.String(), nullable=False),
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["service_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_service_oauth_identities_created_at"),
        "service_oauth_identities",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_oauth_identities_id"), "service_oauth_identities", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_service_oauth_identities_provider"),
        "service_oauth_identities",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_oauth_identities_provider_user"),
        "service_oauth_identities",
        ["provider_user"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_oauth_identities_updated_at"),
        "service_oauth_identities",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "service_thirdparty_tokens",
        sa.Column("identity_id", sa.BIGINT(), nullable=True),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("token_type", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("refresh_after", sa.DateTime(), nullable=False),
        sa.Column("refresh_before", sa.DateTime(), nullable=False),
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["identity_id"],
            ["service_oauth_identities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_service_thirdparty_tokens_created_at"),
        "service_thirdparty_tokens",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_thirdparty_tokens_id"), "service_thirdparty_tokens", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_service_thirdparty_tokens_updated_at"),
        "service_thirdparty_tokens",
        ["updated_at"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_service_thirdparty_tokens_updated_at"), table_name="service_thirdparty_tokens"
    )
    op.drop_index(op.f("ix_service_thirdparty_tokens_id"), table_name="service_thirdparty_tokens")
    op.drop_index(
        op.f("ix_service_thirdparty_tokens_created_at"), table_name="service_thirdparty_tokens"
    )
    op.drop_table("service_thirdparty_tokens")
    op.drop_index(
        op.f("ix_service_oauth_identities_updated_at"), table_name="service_oauth_identities"
    )
    op.drop_index(
        op.f("ix_service_oauth_identities_provider_user"), table_name="service_oauth_identities"
    )
    op.drop_index(
        op.f("ix_service_oauth_identities_provider"), table_name="service_oauth_identities"
    )
    op.drop_index(op.f("ix_service_oauth_identities_id"), table_name="service_oauth_identities")
    op.drop_index(
        op.f("ix_service_oauth_identities_created_at"), table_name="service_oauth_identities"
    )
    op.drop_table("service_oauth_identities")
    # ### end Alembic commands ###
