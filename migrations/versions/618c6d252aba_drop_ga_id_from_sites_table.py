"""Drop ga_id from Sites table

Revision ID: 618c6d252aba
Revises: 6ac51b7ebd2b
Create Date: 2020-09-29 19:11:37.812050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '618c6d252aba'
down_revision = '6ac51b7ebd2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sites', 'ga_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sites', sa.Column('ga_id', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
