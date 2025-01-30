"""empty message

Revision ID: 381da283d416
Revises: 33b072fd84e6
Create Date: 2025-01-29 06:53:59.169276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '381da283d416'
down_revision = '33b072fd84e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('semi_companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_semi_companies_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('semi_companies', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_semi_companies_user_id'))
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
