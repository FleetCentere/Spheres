"""empty message

Revision ID: 7de45b71a25f
Revises: bf013615a0ee
Create Date: 2025-01-02 15:20:42.606246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7de45b71a25f'
down_revision = 'bf013615a0ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workout_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_contents_workout_id'), ['workout_id'], unique=False)
        batch_op.create_foreign_key(None, 'workout_activities', ['workout_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contents', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_contents_workout_id'))
        batch_op.drop_column('workout_id')

    # ### end Alembic commands ###
