"""initial

Revision ID: 0b5475ba8275
Revises: 
Create Date: 2024-10-28 00:59:37.163263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0b5475ba8275'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_roles',
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('default', sa.Boolean(), nullable=False),
    sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_roles_created_at'), 'service_roles', ['created_at'], unique=False)
    op.create_index(op.f('ix_service_roles_id'), 'service_roles', ['id'], unique=False)
    op.create_index(op.f('ix_service_roles_name'), 'service_roles', ['name'], unique=True)
    op.create_index(op.f('ix_service_roles_updated_at'), 'service_roles', ['updated_at'], unique=False)
    op.create_table('service_upload_images',
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('mime_type', sa.String(), nullable=False),
    sa.Column('key', sa.String(), nullable=True),
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_upload_images_created_at'), 'service_upload_images', ['created_at'], unique=False)
    op.create_index(op.f('ix_service_upload_images_id'), 'service_upload_images', ['id'], unique=False)
    op.create_index(op.f('ix_service_upload_images_updated_at'), 'service_upload_images', ['updated_at'], unique=False)
    op.create_table('service_users',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('nickname', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('pseudonym', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('next_offline', sa.DateTime(), nullable=False),
    sa.Column('avatar_id', sa.BIGINT(), nullable=True),
    sa.Column('role_id', sa.BIGINT(), nullable=True),
    sa.Column('local_permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['avatar_id'], ['service_upload_images.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['role_id'], ['service_roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_users_created_at'), 'service_users', ['created_at'], unique=False)
    op.create_index(op.f('ix_service_users_description'), 'service_users', ['description'], unique=False)
    op.create_index(op.f('ix_service_users_email'), 'service_users', ['email'], unique=False)
    op.create_index(op.f('ix_service_users_id'), 'service_users', ['id'], unique=False)
    op.create_index(op.f('ix_service_users_next_offline'), 'service_users', ['next_offline'], unique=False)
    op.create_index(op.f('ix_service_users_nickname'), 'service_users', ['nickname'], unique=False)
    op.create_index(op.f('ix_service_users_pseudonym'), 'service_users', ['pseudonym'], unique=False)
    op.create_index(op.f('ix_service_users_updated_at'), 'service_users', ['updated_at'], unique=False)
    op.create_table('service_tokens',
    sa.Column('owner_id', sa.BIGINT(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('expire_at', sa.DateTime(), nullable=False),
    sa.Column('used_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['service_users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_tokens_body'), 'service_tokens', ['body'], unique=False)
    op.create_index(op.f('ix_service_tokens_created_at'), 'service_tokens', ['created_at'], unique=False)
    op.create_index(op.f('ix_service_tokens_id'), 'service_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_service_tokens_updated_at'), 'service_tokens', ['updated_at'], unique=False)
    op.create_index(op.f('ix_service_tokens_used_at'), 'service_tokens', ['used_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_tokens_used_at'), table_name='service_tokens')
    op.drop_index(op.f('ix_service_tokens_updated_at'), table_name='service_tokens')
    op.drop_index(op.f('ix_service_tokens_id'), table_name='service_tokens')
    op.drop_index(op.f('ix_service_tokens_created_at'), table_name='service_tokens')
    op.drop_index(op.f('ix_service_tokens_body'), table_name='service_tokens')
    op.drop_table('service_tokens')
    op.drop_index(op.f('ix_service_users_updated_at'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_pseudonym'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_nickname'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_next_offline'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_id'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_email'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_description'), table_name='service_users')
    op.drop_index(op.f('ix_service_users_created_at'), table_name='service_users')
    op.drop_table('service_users')
    op.drop_index(op.f('ix_service_upload_images_updated_at'), table_name='service_upload_images')
    op.drop_index(op.f('ix_service_upload_images_id'), table_name='service_upload_images')
    op.drop_index(op.f('ix_service_upload_images_created_at'), table_name='service_upload_images')
    op.drop_table('service_upload_images')
    op.drop_index(op.f('ix_service_roles_updated_at'), table_name='service_roles')
    op.drop_index(op.f('ix_service_roles_name'), table_name='service_roles')
    op.drop_index(op.f('ix_service_roles_id'), table_name='service_roles')
    op.drop_index(op.f('ix_service_roles_created_at'), table_name='service_roles')
    op.drop_table('service_roles')
    # ### end Alembic commands ###