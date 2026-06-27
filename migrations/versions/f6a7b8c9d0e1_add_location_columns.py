"""Add location columns to Plant model

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-06-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('added_lat', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('added_lng', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.drop_column('added_lng')
        batch_op.drop_column('added_lat')
