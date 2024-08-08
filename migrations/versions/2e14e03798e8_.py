"""empty message

Revision ID: 2e14e03798e8
Revises: 6619f60c3973
Create Date: 2024-08-07 19:28:50.890768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e14e03798e8'
down_revision = '6619f60c3973'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('packing_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('list_name', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('packing_list_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('packed_quantity', sa.Integer(), nullable=False),
    sa.Column('is_packed', sa.Boolean(), nullable=True),
    sa.Column('packing_list_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['packing_list_id'], ['packing_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('packing_list_item')
    op.drop_table('packing_list')
    # ### end Alembic commands ###
