"""baseline schema

The schema as created by the old create_all() startup path. Existing
databases without an alembic_version table are stamped at this revision
by app.database.init_db().

Revision ID: 0001
Revises: 
Create Date: 2026-10-19 23:08:50.940086
"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('model_provider', sa.String(length=50), nullable=False),
    sa.Column('model_name', sa.String(length=100), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=True),
    sa.Column('max_tokens', sa.Integer(), nullable=True),
    sa.Column('top_p', sa.Float(), nullable=True),
    sa.Column('message_count', sa.Integer(), nullable=True),
    sa.Column('total_tokens', sa.Integer(), nullable=True),
    sa.Column('extra_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_conversations_id'), ['id'], unique=False)

    op.create_table('model_configs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('api_key', sa.Text(), nullable=True),
    sa.Column('api_base_url', sa.String(length=512), nullable=True),
    sa.Column('organization_id', sa.String(length=255), nullable=True),
    sa.Column('available_models', sa.JSON(), nullable=True),
    sa.Column('default_model', sa.String(length=100), nullable=True),
    sa.Column('default_temperature', sa.Float(), nullable=True),
    sa.Column('default_max_tokens', sa.Integer(), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider')
    )
    with op.batch_alter_table('model_configs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_model_configs_id'), ['id'], unique=False)

    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('prompt_tokens', sa.Integer(), nullable=True),
    sa.Column('completion_tokens', sa.Integer(), nullable=True),
    sa.Column('total_tokens', sa.Integer(), nullable=True),
    sa.Column('extra_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_messages_conversation_id'), ['conversation_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_messages_id'), ['id'], unique=False)

    op.create_table('file_attachments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('original_filename', sa.String(length=255), nullable=False),
    sa.Column('stored_filename', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=512), nullable=False),
    sa.Column('file_type', sa.String(length=50), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('processed', sa.Boolean(), nullable=True),
    sa.Column('processed_content', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stored_filename')
    )
    with op.batch_alter_table('file_attachments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_file_attachments_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_file_attachments_message_id'), ['message_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('file_attachments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_file_attachments_message_id'))
        batch_op.drop_index(batch_op.f('ix_file_attachments_id'))

    op.drop_table('file_attachments')
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_messages_id'))
        batch_op.drop_index(batch_op.f('ix_messages_conversation_id'))

    op.drop_table('messages')
    with op.batch_alter_table('model_configs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_model_configs_id'))

    op.drop_table('model_configs')
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversations_id'))

    op.drop_table('conversations')
