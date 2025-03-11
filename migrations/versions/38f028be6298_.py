"""empty message

Revision ID: 38f028be6298
Revises: 
Create Date: 2025-03-11 22:03:50.029258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38f028be6298'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('manga',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('poster', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=False),
    sa.Column('adult', sa.Integer(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['status.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('manga_artist',
    sa.Column('manga_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], )
    )
    op.create_table('manga_author',
    sa.Column('manga_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], )
    )
    op.create_table('manga_genre',
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.Column('title_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['title_id'], ['manga.id'], )
    )
    op.create_table('manga_name_translation',
    sa.Column('manga_id', sa.Integer(), nullable=True),
    sa.Column('lang', sa.String(length=5), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], )
    )
    op.create_table('manga_publisher',
    sa.Column('manga_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], )
    )
    op.create_table('name_translation',
    sa.Column('manga_id', sa.Integer(), nullable=False),
    sa.Column('lang', sa.String(length=5), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ),
    sa.PrimaryKeyConstraint('manga_id', 'lang')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('login',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=64),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=60),
               type_=sa.String(length=320),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.String(length=320),
               type_=sa.VARCHAR(length=60),
               existing_nullable=False)
        batch_op.alter_column('login',
               existing_type=sa.String(length=64),
               type_=sa.VARCHAR(length=40),
               existing_nullable=False)

    op.drop_table('name_translation')
    op.drop_table('manga_publisher')
    op.drop_table('manga_name_translation')
    op.drop_table('manga_genre')
    op.drop_table('manga_author')
    op.drop_table('manga_artist')
    op.drop_table('manga')
    op.drop_table('type')
    op.drop_table('status')
    op.drop_table('genre')
    # ### end Alembic commands ###
