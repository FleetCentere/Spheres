"""empty message

Revision ID: 1a25a77935e2
Revises: 049b58bf4fb7
Create Date: 2024-11-17 16:25:51.613384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a25a77935e2'
down_revision = '049b58bf4fb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('deleted')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
