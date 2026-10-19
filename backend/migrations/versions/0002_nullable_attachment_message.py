"""file_attachments.message_id nullable

Replaces the old one-off migrate_file_attachments.py script. Databases
that already ran that script are unaffected (the column is already
nullable); older ones get the column relaxed so files can be uploaded
before they are linked to a message.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('file_attachments', schema=None) as batch_op:
        batch_op.alter_column('message_id', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('file_attachments', schema=None) as batch_op:
        batch_op.alter_column('message_id', existing_type=sa.Integer(), nullable=False)
