"""Add compositions

Revision ID: 9b9e4ca98311
Revises: 0b5475ba8275
Create Date: 2024-11-04 13:06:36.164879

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9b9e4ca98311"
down_revision: Union[str, None] = "0b5475ba8275"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "service_compositions",
        sa.Column("preview_id", sa.BIGINT(), nullable=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("style", sa.String(), nullable=False),
        sa.Column("title_original", sa.String(), nullable=False),
        sa.Column("title_en", sa.String(), nullable=True),
        sa.Column("title_uk", sa.String(), nullable=True),
        sa.Column("synopsis_en", sa.String(), nullable=True),
        sa.Column("synopsis_uk", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("nsfw", sa.Boolean(), nullable=False),
        sa.Column("genres", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("chapters", sa.Integer(), nullable=True),
        sa.Column("volumes", sa.Integer(), nullable=True),
        sa.Column("mal_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("provider_id", sa.String(), nullable=True),
        sa.Column("variants", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("scored_by", sa.Integer(), nullable=False),
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["preview_id"], ["service_upload_images.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_service_compositions_chapters"), "service_compositions", ["chapters"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_created_at"),
        "service_compositions",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_id"), "service_compositions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_mal_id"), "service_compositions", ["mal_id"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_nsfw"), "service_compositions", ["nsfw"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_provider"), "service_compositions", ["provider"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_provider_id"),
        "service_compositions",
        ["provider_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_score"), "service_compositions", ["score"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_scored_by"),
        "service_compositions",
        ["scored_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_start_date"),
        "service_compositions",
        ["start_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_style"), "service_compositions", ["style"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_synopsis_en"),
        "service_compositions",
        ["synopsis_en"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_synopsis_uk"),
        "service_compositions",
        ["synopsis_uk"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_title_en"), "service_compositions", ["title_en"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_title_original"),
        "service_compositions",
        ["title_original"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_title_uk"), "service_compositions", ["title_uk"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_updated_at"),
        "service_compositions",
        ["updated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_compositions_variants"), "service_compositions", ["variants"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_volumes"), "service_compositions", ["volumes"], unique=False
    )
    op.create_index(
        op.f("ix_service_compositions_year"), "service_compositions", ["year"], unique=False
    )
    op.create_table(
        "service_composition_variants",
        sa.Column("origin_id", sa.BIGINT(), nullable=True),
        sa.Column("author_id", sa.BIGINT(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("title_local", sa.String(), nullable=True),
        sa.Column("synopsis_local", sa.String(), nullable=True),
        sa.Column("chapters", sa.Integer(), nullable=False),
        sa.Column("volumes", sa.Integer(), nullable=False),
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["service_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["origin_id"], ["service_compositions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_service_composition_variants_chapters"),
        "service_composition_variants",
        ["chapters"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_created_at"),
        "service_composition_variants",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_id"),
        "service_composition_variants",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_status"),
        "service_composition_variants",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_synopsis_local"),
        "service_composition_variants",
        ["synopsis_local"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_title_local"),
        "service_composition_variants",
        ["title_local"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_updated_at"),
        "service_composition_variants",
        ["updated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_service_composition_variants_volumes"),
        "service_composition_variants",
        ["volumes"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_service_composition_variants_volumes"), table_name="service_composition_variants"
    )
    op.drop_index(
        op.f("ix_service_composition_variants_updated_at"),
        table_name="service_composition_variants",
    )
    op.drop_index(
        op.f("ix_service_composition_variants_title_local"),
        table_name="service_composition_variants",
    )
    op.drop_index(
        op.f("ix_service_composition_variants_synopsis_local"),
        table_name="service_composition_variants",
    )
    op.drop_index(
        op.f("ix_service_composition_variants_status"), table_name="service_composition_variants"
    )
    op.drop_index(
        op.f("ix_service_composition_variants_id"), table_name="service_composition_variants"
    )
    op.drop_index(
        op.f("ix_service_composition_variants_created_at"),
        table_name="service_composition_variants",
    )
    op.drop_index(
        op.f("ix_service_composition_variants_chapters"), table_name="service_composition_variants"
    )
    op.drop_table("service_composition_variants")
    op.drop_index(op.f("ix_service_compositions_year"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_volumes"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_variants"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_updated_at"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_title_uk"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_title_original"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_title_en"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_synopsis_uk"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_synopsis_en"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_style"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_start_date"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_scored_by"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_score"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_provider_id"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_provider"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_nsfw"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_mal_id"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_id"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_created_at"), table_name="service_compositions")
    op.drop_index(op.f("ix_service_compositions_chapters"), table_name="service_compositions")
    op.drop_table("service_compositions")
    # ### end Alembic commands ###
