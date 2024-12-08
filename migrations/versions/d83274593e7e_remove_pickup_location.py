"""remove pickup_location

Revision ID: d83274593e7e
Revises: 8580834e811c
Create Date: 2024-12-01 23:57:28.815669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd83274593e7e'
down_revision = '8580834e811c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_delivery')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_alembic_tmp_delivery',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('delivery_location', sa.VARCHAR(length=100), nullable=False),
    sa.Column('status', sa.VARCHAR(length=20), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('item_description', sa.VARCHAR(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###