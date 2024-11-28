"""Rename product_type to user_name

Revision ID: 8580834e811c
Revises: 
Create Date: 2024-11-19 19:39:11.315770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8580834e811c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('navigation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_name', sa.String(length=200), nullable=True))
        batch_op.drop_column('product_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('navigation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_type', sa.VARCHAR(length=200), nullable=False))
        batch_op.drop_column('user_name')

    # ### end Alembic commands ###
