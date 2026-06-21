"""Remove photo_filename and widen string columns

Revision ID: b1c2d3e4f5a6
Revises: 0a7f1bb615a3
Create Date: 2026-06-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = '0a7f1bb615a3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.drop_column('photo_filename')
        batch_op.alter_column('name', existing_type=sa.String(100), type_=sa.String(256))
        batch_op.alter_column('wiki_link', existing_type=sa.String(200), type_=sa.String(512))
        batch_op.alter_column('image_source_url', existing_type=sa.String(200), type_=sa.String(2048))
        batch_op.alter_column('scientific_name', existing_type=sa.String(100), type_=sa.String(256))


def downgrade():
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.alter_column('name', existing_type=sa.String(256), type_=sa.String(100))
        batch_op.alter_column('wiki_link', existing_type=sa.String(512), type_=sa.String(200))
        batch_op.alter_column('image_source_url', existing_type=sa.String(2048), type_=sa.String(200))
        batch_op.alter_column('scientific_name', existing_type=sa.String(256), type_=sa.String(100))
        batch_op.add_column(sa.Column('photo_filename', sa.String(100), nullable=True))
