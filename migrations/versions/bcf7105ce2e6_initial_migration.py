"""Initial migration

Revision ID: bcf7105ce2e6
Revises: 
Create Date: 2024-02-03 22:55:32.353707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcf7105ce2e6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=128), nullable=False),
    sa.Column('language', sa.String(length=10), nullable=False),
    sa.Column('joined_at', sa.TIMESTAMP(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('last_activity', sa.TIMESTAMP(), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('notify_hours', sa.ARRAY(sa.SMALLINT()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('type', sa.Enum('SLEEP', 'WORK', 'STUDYING', 'FAMILY', 'FRIENDS', 'PASSIVE', 'EXERCISE', 'READING', name='activitytypes'), nullable=False),
    sa.Column('time', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('actions')
    op.drop_table('users')
    # ### end Alembic commands ###