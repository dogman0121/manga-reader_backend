"""empty message

Revision ID: b0ef0ce6caa0
Revises: c19d3caa47ee
Create Date: 2025-07-03 19:03:15.586605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0ef0ce6caa0'
down_revision = 'c19d3caa47ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(), nullable=False))
        batch_op.create_unique_constraint(None, ['slug'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('slug')

    # ### end Alembic commands ###
