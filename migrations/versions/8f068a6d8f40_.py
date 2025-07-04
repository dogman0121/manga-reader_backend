"""empty message

Revision ID: 8f068a6d8f40
Revises: 78019db2d85e
Create Date: 2025-07-03 19:08:09.556260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f068a6d8f40'
down_revision = '78019db2d85e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.alter_column('slug',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.alter_column('slug',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
