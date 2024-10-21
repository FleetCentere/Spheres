"""new fields in user model like avatar, about_me and last_seen

Revision ID: 227762e6c9f8
Revises: 9b3e41a086e4
Create Date: 2024-10-20 14:54:15.183624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '227762e6c9f8'
down_revision = '9b3e41a086e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_me', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('about_me')

    # ### end Alembic commands ###