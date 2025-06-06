"""empty message

Revision ID: 238182f0522c
Revises: fe0198212d99
Create Date: 2025-05-03 15:14:59.696745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '238182f0522c'
down_revision = 'fe0198212d99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chapter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('manga_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'manga', ['manga_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chapter', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('manga_id')

    # ### end Alembic commands ###
