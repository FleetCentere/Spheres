"""empty message

Revision ID: b8b7490a7100
Revises: 7de45b71a25f
Create Date: 2025-01-07 19:08:15.872589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8b7490a7100'
down_revision = '7de45b71a25f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('statement', sa.String(length=140), nullable=False),
    sa.Column('check_date', sa.DateTime(), nullable=False),
    sa.Column('associated_content', sa.String(length=256), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('predictions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_predictions_user_id'), ['user_id'], unique=False)

    op.create_table('prediction_tags',
    sa.Column('prediction_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('prediction_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prediction_tags')
    with op.batch_alter_table('predictions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_predictions_user_id'))

    op.drop_table('predictions')
    # ### end Alembic commands ###
