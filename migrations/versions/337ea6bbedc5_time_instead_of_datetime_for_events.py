"""time instead of datetime for events

Revision ID: 337ea6bbedc5
Revises: cd09567443b5
Create Date: 2024-12-05 07:16:30.652553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '337ea6bbedc5'
down_revision = 'cd09567443b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Time(),
               existing_nullable=False)
        batch_op.alter_column('end_time',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Time(),
               existing_nullable=False)

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

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('end_time',
               existing_type=sa.Time(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
        batch_op.alter_column('start_time',
               existing_type=sa.Time(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    # ### end Alembic commands ###