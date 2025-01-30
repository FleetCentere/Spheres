"""empty message

Revision ID: 33b072fd84e6
Revises: 01b71e2e3109
Create Date: 2025-01-28 19:18:21.455439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33b072fd84e6'
down_revision = '01b71e2e3109'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('semi_companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('ticker', sa.String(length=10), nullable=False),
    sa.Column('general_industry', sa.String(length=100), nullable=False),
    sa.Column('specific_industry', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('country', sa.String(length=100), nullable=False),
    sa.Column('revenue_2025', sa.Float(), nullable=True),
    sa.Column('revenue_2024', sa.Float(), nullable=True),
    sa.Column('revenue_2023', sa.Float(), nullable=True),
    sa.Column('revenue_2022', sa.Float(), nullable=True),
    sa.Column('revenue_2025_q1', sa.Float(), nullable=True),
    sa.Column('revenue_2024_q4', sa.Float(), nullable=True),
    sa.Column('revenue_2024_q3', sa.Float(), nullable=True),
    sa.Column('revenue_2024_q2', sa.Float(), nullable=True),
    sa.Column('revenue_2024_q1', sa.Float(), nullable=True),
    sa.Column('labor_costs_2025', sa.Float(), nullable=True),
    sa.Column('labor_costs_2024', sa.Float(), nullable=True),
    sa.Column('labor_costs_2023', sa.Float(), nullable=True),
    sa.Column('labor_costs_2022', sa.Float(), nullable=True),
    sa.Column('labor_costs_2025_q1', sa.Float(), nullable=True),
    sa.Column('labor_costs_2024_q4', sa.Float(), nullable=True),
    sa.Column('labor_costs_2024_q3', sa.Float(), nullable=True),
    sa.Column('labor_costs_2024_q2', sa.Float(), nullable=True),
    sa.Column('labor_costs_2024_q1', sa.Float(), nullable=True),
    sa.Column('cogs_2025', sa.Float(), nullable=True),
    sa.Column('cogs_2024', sa.Float(), nullable=True),
    sa.Column('cogs_2023', sa.Float(), nullable=True),
    sa.Column('cogs_2022', sa.Float(), nullable=True),
    sa.Column('cogs_2025_q1', sa.Float(), nullable=True),
    sa.Column('cogs_2024_q4', sa.Float(), nullable=True),
    sa.Column('cogs_2024_q3', sa.Float(), nullable=True),
    sa.Column('cogs_2024_q2', sa.Float(), nullable=True),
    sa.Column('cogs_2024_q1', sa.Float(), nullable=True),
    sa.Column('capex_2025', sa.Float(), nullable=True),
    sa.Column('capex_2024', sa.Float(), nullable=True),
    sa.Column('capex_2023', sa.Float(), nullable=True),
    sa.Column('capex_2022', sa.Float(), nullable=True),
    sa.Column('capex_2025_q1', sa.Float(), nullable=True),
    sa.Column('capex_2024_q4', sa.Float(), nullable=True),
    sa.Column('capex_2024_q3', sa.Float(), nullable=True),
    sa.Column('capex_2024_q2', sa.Float(), nullable=True),
    sa.Column('capex_2024_q1', sa.Float(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('semi_companies', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_semi_companies_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_semi_companies_ticker'), ['ticker'], unique=True)

    op.create_table('company_customers',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['semi_companies.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['semi_companies.id'], ),
    sa.PrimaryKeyConstraint('company_id', 'customer_id')
    )
    op.create_table('company_suppliers',
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['semi_companies.id'], ),
    sa.ForeignKeyConstraint(['supplier_id'], ['semi_companies.id'], ),
    sa.PrimaryKeyConstraint('company_id', 'supplier_id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('semi_company_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_posts_semi_company_id'), ['semi_company_id'], unique=False)
        batch_op.create_foreign_key(None, 'semi_companies', ['semi_company_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_posts_semi_company_id'))
        batch_op.drop_column('semi_company_id')

    op.drop_table('company_suppliers')
    op.drop_table('company_customers')
    with op.batch_alter_table('semi_companies', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_semi_companies_ticker'))
        batch_op.drop_index(batch_op.f('ix_semi_companies_name'))

    op.drop_table('semi_companies')
    # ### end Alembic commands ###
