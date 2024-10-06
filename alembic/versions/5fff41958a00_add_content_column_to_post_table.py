"""add content column to post table

Revision ID: 5fff41958a00
Revises: 69b8c23b80f0
Create Date: 2024-10-06 11:38:17.292148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fff41958a00'
down_revision: Union[str, None] = '69b8c23b80f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
