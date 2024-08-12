"""Initial migration

Revision ID: 920566015f2f
Revises: 
Create Date: 2024-08-09 14:23:29.003598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '920566015f2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('expense',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('packing_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listName', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('dateSaved', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('packed', sa.Boolean(), nullable=True),
    sa.Column('listId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['listId'], ['packing_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item')
    op.drop_table('packing_list')
    op.drop_table('expense')
    op.drop_table('user')
    # ### end Alembic commands ###
