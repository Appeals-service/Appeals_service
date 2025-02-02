"""empty message

Revision ID: 316db95bb656
Revises: 
Create Date: 2025-02-02 14:29:47.319038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '316db95bb656'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('appeals',
    sa.Column('user', sa.UUID(), nullable=False, comment='User'),
    sa.Column('message', sa.Text(), nullable=False, comment='Appeals text'),
    sa.Column('photo', sa.ARRAY(sa.String()), nullable=True, comment='Appeals photo'),
    sa.Column('responsibility_area', sa.Enum('housing', 'road', 'administration', 'law_enforcement', 'other', name='appealresponsibilityarea'), nullable=False, comment='Appeal responsibility area'),
    sa.Column('executor', sa.UUID(), nullable=True, comment='Executor'),
    sa.Column('status', sa.Enum('accepted', 'in_progress', 'done', 'cancelled', 'rejected', name='appealstatus'), nullable=False, comment='Appeal status'),
    sa.Column('comment', sa.Text(), nullable=True, comment='Comment from executor'),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='Identifier'),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Creation datetime'),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Update datetime'),
    sa.PrimaryKeyConstraint('id', name=op.f('PK_appeals')),
    schema='appeals_service'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appeals', schema='appeals_service')
    op.execute("DROP TYPE IF EXISTS appealresponsibilityarea, appealstatus;")
    # ### end Alembic commands ###
