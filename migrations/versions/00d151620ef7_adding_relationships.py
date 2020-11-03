"""Adding relationships

Revision ID: 00d151620ef7
Revises: 618c6d252aba
Create Date: 2020-09-30 18:59:52.085539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00d151620ef7'
down_revision = '618c6d252aba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('site_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'events', 'sites', ['site_id'], ['id'])
    op.add_column('visits', sa.Column('site_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'visits', 'sites', ['site_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'visits', type_='foreignkey')
    op.drop_column('visits', 'site_id')
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_column('events', 'site_id')
    # ### end Alembic commands ###
