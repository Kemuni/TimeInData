"""Add notify hours to user

Revision ID: d16133351916
Revises: 9944e048a9da
Create Date: 2024-01-04 01:51:59.414130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd16133351916'
down_revision: Union[str, None] = '9944e048a9da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('notify_hours', sa.ARRAY(sa.SMALLINT()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'notify_hours')
    # ### end Alembic commands ###
