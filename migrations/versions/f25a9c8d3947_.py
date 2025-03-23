"""empty message

Revision ID: f25a9c8d3947
Revises: d12e4adcbb09
Create Date: 2025-03-23 15:52:10.340337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f25a9c8d3947'
down_revision = 'd12e4adcbb09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('manga_background')
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('manga', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    op.create_table('manga_background',
    sa.Column('manga_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('filename', sa.TEXT(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('filename', name='manga_background_pkey')
    )
    # ### end Alembic commands ###
