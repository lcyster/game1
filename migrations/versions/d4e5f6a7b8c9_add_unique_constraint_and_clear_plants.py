"""Add unique constraint on scientific_name and clear plants

Revision ID: d4e5f6a7b8c9
Revises: 0a7f1bb615a3
Create Date: 2026-06-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b8c9'
down_revision = 'c2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DELETE FROM plant')
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_plant_scientific_name', ['scientific_name'])


def downgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.drop_constraint('uq_plant_scientific_name', type_='unique')
