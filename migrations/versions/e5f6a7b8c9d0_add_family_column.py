"""Add family column to Plant model

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('family', sa.String(length=256), nullable=True))


def downgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.drop_column('family')
