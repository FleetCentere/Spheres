"""empty message

Revision ID: a19894198300
Revises: 337ea6bbedc5
Create Date: 2024-12-18 09:35:04.892852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a19894198300'
down_revision = '337ea6bbedc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tags_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_tags_user_id'), ['user_id'], unique=False)

    op.create_table('content_tags',
    sa.Column('content_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['content_id'], ['contents.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('content_id', 'tag_id')
    )
    op.create_table('event_tags',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'tag_id')
    )
    op.create_table('post_tags',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('post_id', 'tag_id')
    )
    op.create_table('task_tags',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )
    op.drop_table('post_references')
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=140),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=140),
               nullable=True)

    op.create_table('post_references',
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('referenced_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('referenced_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='post_references_post_id_fkey'),
    sa.PrimaryKeyConstraint('post_id', 'referenced_id', 'referenced_type', name='post_references_pkey')
    )
    op.drop_table('task_tags')
    op.drop_table('post_tags')
    op.drop_table('event_tags')
    op.drop_table('content_tags')
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tags_user_id'))
        batch_op.drop_index(batch_op.f('ix_tags_timestamp'))

    op.drop_table('tags')
    # ### end Alembic commands ###
