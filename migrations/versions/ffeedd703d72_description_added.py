"""description added

Revision ID: ffeedd703d72
Revises: 5c3f7fd619c6
Create Date: 2020-07-09 13:26:56.362361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffeedd703d72'
down_revision = '5c3f7fd619c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('poll', sa.Column('description', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_poll_description'), 'poll', ['description'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_poll_description'), table_name='poll')
    op.drop_column('poll', 'description')
    # ### end Alembic commands ###
